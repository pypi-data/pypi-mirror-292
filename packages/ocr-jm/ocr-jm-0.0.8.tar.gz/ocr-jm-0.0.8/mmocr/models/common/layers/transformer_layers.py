# Copyright (c) OpenMMLab. All rights reserved.
import torch.nn as nn
from mmengine.model import BaseModule

from mmocr.models.common.modules import (MultiHeadAttention,
                                         PositionwiseFeedForward)


# from performer_pytorch import SelfAttention, CrossAttention
# from mmocr.models.common.layers.performer_layers import SelfAttention, CrossAttention

class TFEncoderLayer(BaseModule):
    """Transformer Encoder Layer.

    Args:
        d_model (int): The number of expected features
            in the decoder inputs (default=512).
        d_inner (int): The dimension of the feedforward
            network model (default=256).
        n_head (int): The number of heads in the
            multiheadattention models (default=8).
        d_k (int): Total number of features in key.
        d_v (int): Total number of features in value.
        dropout (float): Dropout layer on attn_output_weights.
        qkv_bias (bool): Add bias in projection layer. Default: False.
        act_cfg (dict): Activation cfg for feedforward module.
        operation_order (tuple[str]): The execution order of operation
            in transformer. Such as ('self_attn', 'norm', 'ffn', 'norm')
            or ('norm', 'self_attn', 'norm', 'ffn').
            Default：None.
    """

    def __init__(self,
                 d_model=512,
                 d_inner=256,
                 n_head=8,
                 d_k=64,
                 d_v=64,
                 dropout=0.1,
                 qkv_bias=False,
                 act_cfg=dict(type='mmengine.GELU'),
                 operation_order=None):
        super().__init__()
        self.attn = MultiHeadAttention(
            n_head, d_model, d_k, d_v, qkv_bias=qkv_bias, dropout=dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.mlp = PositionwiseFeedForward(
            d_model, d_inner, dropout=dropout, act_cfg=act_cfg)
        self.norm2 = nn.LayerNorm(d_model)

        self.operation_order = operation_order
        if self.operation_order is None:
            self.operation_order = ('norm', 'self_attn', 'norm', 'ffn')

        assert self.operation_order in [('norm', 'self_attn', 'norm', 'ffn'),
                                        ('self_attn', 'norm', 'ffn', 'norm')]

    def forward(self, x, mask=None):
        if self.operation_order == ('self_attn', 'norm', 'ffn', 'norm'):
            residual = x
            x = residual + self.attn(x, x, x, mask)
            x = self.norm1(x)

            residual = x
            x = residual + self.mlp(x)
            x = self.norm2(x)
        elif self.operation_order == ('norm', 'self_attn', 'norm', 'ffn'):
            residual = x
            x = self.norm1(x)
            x = residual + self.attn(x, x, x, mask)

            residual = x
            x = self.norm2(x)
            x = residual + self.mlp(x)

        return x


class TFDecoderLayer(nn.Module):
    """Transformer Decoder Layer.

    Args:
        d_model (int): The number of expected features
            in the decoder inputs (default=512).
        d_inner (int): The dimension of the feedforward
            network model (default=256).
        n_head (int): The number of heads in the
            multiheadattention models (default=8).
        d_k (int): Total number of features in key.
        d_v (int): Total number of features in value.
        dropout (float): Dropout layer on attn_output_weights.
        qkv_bias (bool): Add bias in projection layer. Default: False.
        act_cfg (dict): Activation cfg for feedforward module.
        operation_order (tuple[str]): The execution order of operation
            in transformer. Such as ('self_attn', 'norm', 'enc_dec_attn',
            'norm', 'ffn', 'norm') or ('norm', 'self_attn', 'norm',
            'enc_dec_attn', 'norm', 'ffn').
            Default：None.
    """

    def __init__(self,
                 d_model=512,
                 d_inner=256,
                 n_head=8,
                 d_k=64,
                 d_v=64,
                 dropout=0.1,
                 qkv_bias=False,
                 act_cfg=dict(type='mmengine.GELU'),
                 operation_order=None,
                 d_embedding=0,
                 d_enc=-1
                 ):
        super().__init__()

        if isinstance(n_head, tuple):
            self.norm1 = nn.LayerNorm(d_embedding)  # since decoder_input dim and encoder_output dim is different
            self.norm2 = nn.LayerNorm(d_embedding)
            self.norm3 = nn.LayerNorm(d_embedding)
            self.self_attn = MultiHeadAttention(
                n_head[0], d_embedding, d_k // n_head[0], d_v // n_head[0], dropout=dropout, qkv_bias=qkv_bias)
            self.enc_attn = MultiHeadAttention(
                n_head[1], d_embedding, d_k // n_head[1], d_v // n_head[1], dropout=dropout, qkv_bias=qkv_bias,
                cross_attn=True, d_enc=d_enc)
            self.mlp = PositionwiseFeedForward(
                d_embedding, d_inner, dropout=dropout, act_cfg=act_cfg)
        else:
            self.norm1 = nn.LayerNorm(d_model)
            self.norm2 = nn.LayerNorm(d_model)
            self.norm3 = nn.LayerNorm(d_model)
            self.self_attn = MultiHeadAttention(
                n_head, d_model, d_k, d_v, dropout=dropout, qkv_bias=qkv_bias)
            self.enc_attn = MultiHeadAttention(
                n_head, d_model, d_k, d_v, dropout=dropout, qkv_bias=qkv_bias)

            self.mlp = PositionwiseFeedForward(
                d_model, d_inner, dropout=dropout, act_cfg=act_cfg)

        self.operation_order = operation_order
        if self.operation_order is None:
            self.operation_order = ('norm', 'self_attn', 'norm',
                                    'enc_dec_attn', 'norm', 'ffn')
        assert self.operation_order in [
            ('norm', 'self_attn', 'norm', 'enc_dec_attn', 'norm', 'ffn'),
            ('self_attn', 'norm', 'enc_dec_attn', 'norm', 'ffn', 'norm')
        ]

    def forward(self,
                dec_input,
                enc_output,
                self_attn_mask=None,
                dec_enc_attn_mask=None):
        if self.operation_order == ('self_attn', 'norm', 'enc_dec_attn',
                                    'norm', 'ffn', 'norm'):

            dec_attn_out = self.self_attn(dec_input, dec_input,
                                          dec_input, self_attn_mask)
            dec_attn_out += dec_input
            dec_attn_out = self.norm1(dec_attn_out)

            enc_dec_attn_out = self.enc_attn(dec_attn_out, enc_output,
                                             enc_output, dec_enc_attn_mask)
            enc_dec_attn_out += dec_attn_out
            enc_dec_attn_out = self.norm2(enc_dec_attn_out)

            mlp_out = self.mlp(enc_dec_attn_out)
            mlp_out += enc_dec_attn_out
            mlp_out = self.norm3(mlp_out)
        elif self.operation_order == ('norm', 'self_attn', 'norm',
                                      'enc_dec_attn', 'norm', 'ffn'):
            dec_input_norm = self.norm1(dec_input)
            dec_attn_out = self.self_attn(dec_input_norm, dec_input_norm,
                                          dec_input_norm, self_attn_mask)
            dec_attn_out += dec_input

            enc_dec_attn_in = self.norm2(dec_attn_out)
            enc_dec_attn_out = self.enc_attn(enc_dec_attn_in, enc_output,
                                             enc_output, dec_enc_attn_mask)
            enc_dec_attn_out += dec_attn_out

            mlp_out = self.mlp(self.norm3(enc_dec_attn_out))
            mlp_out += enc_dec_attn_out

        return mlp_out


class Cached_TFDecoderLayer(TFDecoderLayer):
    """Transformer Decoder Layer.

    Args:
        d_model (int): The number of expected features
            in the decoder inputs (default=512).
        d_inner (int): The dimension of the feedforward
            network model (default=256).
        n_head (int): The number of heads in the
            multiheadattention models (default=8).
        d_k (int): Total number of features in key.
        d_v (int): Total number of features in value.
        dropout (float): Dropout layer on attn_output_weights.
        qkv_bias (bool): Add bias in projection layer. Default: False.
        act_cfg (dict): Activation cfg for feedforward module.
        operation_order (tuple[str]): The execution order of operation
            in transformer. Such as ('self_attn', 'norm', 'enc_dec_attn',
            'norm', 'ffn', 'norm') or ('norm', 'self_attn', 'norm',
            'enc_dec_attn', 'norm', 'ffn').
            Default：None.
    """

    def __init__(self,
                 d_model=512,
                 d_inner=256,
                 n_head=8,
                 d_k=64,
                 d_v=64,
                 dropout=0.1,
                 qkv_bias=False,
                 act_cfg=dict(type='mmengine.GELU'),
                 operation_order=None,
                 d_embedding=0,
                 d_enc=-1
                 ):

        super().__init__(d_model, d_inner, n_head, d_k, d_v, dropout, qkv_bias, act_cfg, operation_order, d_embedding,
                         d_enc)

        self.self_attn.caching = True
        self.enc_attn.caching = True
        self.enc_attn.cross_attn = True

    def forward(self,
                dec_input,
                enc_output,
                self_attn_mask=None,
                dec_enc_attn_mask=None,
                cache=None):

        if cache is None:
            cache = {}

        if self.operation_order == ('self_attn', 'norm', 'enc_dec_attn',
                                    'norm', 'ffn', 'norm'):
            last_tok = dec_input[:, -1:,
                       :]  # only the last token gets modified and returned. final token is for end token
            dec_attn_out, new_cache = self.self_attn(last_tok, dec_input,
                                                     dec_input, mask=None, cache=cache)
            last_tok += dec_attn_out
            last_tok = self.norm1(last_tok)

            enc_dec_attn_out, new_cache = self.enc_attn(last_tok, enc_output,
                                                        enc_output, dec_enc_attn_mask)

            last_tok += enc_dec_attn_out
            last_tok = self.norm2(last_tok)

            mlp_out = self.mlp(last_tok)
            mlp_out += last_tok
            mlp_out = self.norm3(mlp_out)
        elif self.operation_order == ('norm', 'self_attn', 'norm',
                                      'enc_dec_attn', 'norm', 'ffn'):
            dec_input_norm = self.norm1(dec_input)
            dec_attn_out = self.self_attn(dec_input_norm, dec_input_norm,
                                          dec_input_norm, mask=None, cache=cache)

            dec_attn_out += dec_input

            enc_dec_attn_in = self.norm2(dec_attn_out)
            enc_dec_attn_out = self.enc_attn(enc_dec_attn_in, enc_output,
                                             enc_output, dec_enc_attn_mask, cache=cache)

            enc_dec_attn_out += dec_attn_out

            mlp_out = self.mlp(self.norm3(enc_dec_attn_out))
            mlp_out += enc_dec_attn_out

        return mlp_out, cache
