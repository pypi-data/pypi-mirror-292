# Copyright (c) OpenMMLab. All rights reserved.
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from mmocr.registry import MODELS


class ScaledDotProductAttention(nn.Module):
    """Scaled Dot-Product Attention Module. This code is adopted from
    https://github.com/jadore801120/attention-is-all-you-need-pytorch.

    Args:
        temperature (float): The scale factor for softmax input.
        attn_dropout (float): Dropout layer on attn_output_weights.
    """

    def __init__(self, temperature, attn_dropout=0.1):
        super().__init__()
        self.temperature = temperature
        self.dropout = nn.Dropout(attn_dropout)

    def forward(self, q, k, v, mask=None):
        attn = torch.matmul(q / self.temperature, k.transpose(2, 3))

        if mask is not None:
            attn = attn.masked_fill(mask == 0, float('-inf'))

        attn = self.dropout(F.softmax(attn, dim=-1))

        output = torch.matmul(attn, v)

        return output, attn


class MultiHeadAttention(nn.Module):
    """Multi-Head Attention module.

    Args:
        n_head (int): The number of heads in the
            multiheadattention models (default=8).
        d_model (int): The number of expected features
            in the decoder inputs (default=512).
        d_k (int): Total number of features in key.
        d_v (int): Total number of features in value.
        dropout (float): Dropout layer on attn_output_weights.
        qkv_bias (bool): Add bias in projection layer. Default: False.
    """

    def __init__(self,
                 n_head=8,
                 d_model=512,
                 d_k=64,
                 d_v=64,
                 dropout=0.1,
                 qkv_bias=False,
                 cross_attn=False,
                 d_enc=-1,
                 caching=False):
        super().__init__()
        self.n_head = n_head
        self.d_k = d_k
        self.d_v = d_v
        self.d_enc = d_enc

        self.dim_k = n_head * d_k
        self.dim_v = n_head * d_v
        if d_model != self.dim_k:
            self.linear_q = nn.Linear(d_model, self.dim_k, bias=qkv_bias)
            if cross_attn:
                if self.d_enc == -1: self.d_enc = self.dim_k

                self.linear_k = nn.Linear(self.d_enc, self.dim_k, bias=qkv_bias)
                self.linear_v = nn.Linear(
                    self.d_enc, self.dim_v, bias=qkv_bias)
            else:
                self.linear_k = nn.Linear(d_model, self.dim_k, bias=qkv_bias)
                self.linear_v = nn.Linear(d_model, self.dim_v, bias=qkv_bias)
        else:
            self.linear_q = nn.Linear(self.dim_k, self.dim_k, bias=qkv_bias)
            self.linear_k = nn.Linear(self.dim_k, self.dim_k, bias=qkv_bias)
            self.linear_v = nn.Linear(self.dim_v, self.dim_v, bias=qkv_bias)

        self.attention = ScaledDotProductAttention(d_k ** 0.5, dropout)

        self.fc = nn.Linear(self.dim_v, d_model, bias=qkv_bias)
        self.proj_drop = nn.Dropout(dropout)

        # added for caching
        self.cross_attn = cross_attn
        self.caching = caching

    def _use_saved_state(self, k, v, saved_state, static_kv, batch_size):
        # k, v shape: (B, H, T, D)
        # saved states are stored with shape (bsz, num_heads, seq_len, head_dim)
        if "prev_key" in saved_state:
            _prev_key = saved_state["prev_key"]
            assert _prev_key is not None
            prev_key = _prev_key.view(batch_size, self.n_head, -1, self.d_k)
            if static_kv:
                k = prev_key
            else:
                assert k is not None
                k = torch.cat([prev_key, k], dim=2)
        if "prev_value" in saved_state:
            _prev_value = saved_state["prev_value"]
            assert _prev_value is not None
            prev_value = _prev_value.view(batch_size, self.n_head, -1, self.d_v)
            if static_kv:
                v = prev_value
            else:
                assert v is not None
                v = torch.cat([prev_value, v], dim=2)
        assert k is not None and v is not None
        # prev_key_padding_mask: Optional[Tensor] = saved_state.get("prev_key_padding_mask", None)
        # if prev_key_padding_mask is not None:
        #     if static_kv:
        #         new_key_padding_mask = prev_key_padding_mask
        #     else:
        #         new_key_padding_mask = torch.cat([prev_key_padding_mask, key_padding_mask], dim=1)
        # else:
        #     new_key_padding_mask = key_padding_mask
        return k, v

    def forward(self, q, k, v, mask=None, cache=None):
        batch_size, len_q, _ = q.size()
        _, len_k, _ = k.size()

        self.cache_key = 'cross' if self.cross_attn else 'self'

        if self.caching:
            if cache is not None:
                saved_state = cache.get(self.cache_key, {})
                if 'prev_key' in saved_state and self.cross_attn:
                    k = None
            else:
                saved_state = None
                cache = {}
        q = self.linear_q(q).view(batch_size, len_q, self.n_head, self.d_k)
        q = q.transpose(1, 2)

        if k is None:
            v = None
        else:
            k = self.linear_k(k)
            v = self.linear_v(v)

            k = k.view(batch_size, len_k, self.n_head, self.d_k)
            k = k.transpose(1, 2)  # (B, H, T, D)

            v = v.view(batch_size, len_k, self.n_head, self.d_v)
            v = v.transpose(1, 2)  # (B, H, T, D)

        if self.caching:
            if saved_state is not None:
                k, v = self._use_saved_state(k, v, saved_state, self.cross_attn, batch_size)

            # update cache
            cache[self.cache_key] = {
                "prev_key": k.view(batch_size, self.n_head, -1, self.d_k),
                "prev_value": v.view(batch_size, self.n_head, -1, self.d_k),
            }
            assert k is not None

        if mask is not None:
            if mask.dim() == 3:
                mask = mask.unsqueeze(1)
            elif mask.dim() == 2:
                mask = mask.unsqueeze(1).unsqueeze(1)

        attn_out, _ = self.attention(q, k, v, mask=mask)
        attn_out = attn_out.transpose(1, 2).contiguous().view(
            batch_size, len_q, self.dim_v)

        attn_out = self.fc(attn_out)
        attn_out = self.proj_drop(attn_out)

        return attn_out


class PositionwiseFeedForward(nn.Module):
    """Two-layer feed-forward module.

    Args:
        d_in (int): The dimension of the input for feedforward
            network model.
        d_hid (int): The dimension of the feedforward
            network model.
        dropout (float): Dropout layer on feedforward output.
        act_cfg (dict): Activation cfg for feedforward module.
    """

    def __init__(self, d_in, d_hid, dropout=0.1, act_cfg=dict(type='Relu')):
        super().__init__()
        self.w_1 = nn.Linear(d_in, d_hid)
        self.w_2 = nn.Linear(d_hid, d_in)
        self.act = MODELS.build(act_cfg)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = self.w_1(x)
        x = self.act(x)
        x = self.w_2(x)
        x = self.dropout(x)

        return x


class PositionalEncoding(nn.Module):
    """Fixed positional encoding with sine and cosine functions."""

    def __init__(self, d_hid=512, n_position=200, dropout=0, caching=False):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Not a parameter
        # Position table of shape (1, n_position, d_hid)
        self.register_buffer(
            'position_table',
            self._get_sinusoid_encoding_table(n_position, d_hid))

        self.caching = caching

    def _get_sinusoid_encoding_table(self, n_position, d_hid):
        """Sinusoid position encoding table."""
        denominator = torch.Tensor([
            1.0 / np.power(10000, 2 * (hid_j // 2) / d_hid)
            for hid_j in range(d_hid)
        ])
        denominator = denominator.view(1, -1)
        pos_tensor = torch.arange(n_position).unsqueeze(-1).float()
        sinusoid_table = pos_tensor * denominator
        sinusoid_table[:, 0::2] = torch.sin(sinusoid_table[:, 0::2])
        sinusoid_table[:, 1::2] = torch.cos(sinusoid_table[:, 1::2])

        return sinusoid_table.unsqueeze(0)

    # def forward(self, x, len_seq=1, caching=False):
    def forward(self, x):
        """
        Args:
            x (Tensor): Tensor of shape (batch_size, pos_len, d_hid, ...)
        """
        # self.caching = caching
        self.device = x.device
        if self.caching:
            len_seq = x.shape[1]
            x = x[:, -1:]
            x = x + self.position_table[:, len_seq - 1].clone().detach()
        else:
            x = x + self.position_table[:, :x.size(1)].clone().detach()
        return self.dropout(x)
