# Copyright (c) OpenMMLab. All rights reserved.
import math
from typing import Dict, List, Optional, Sequence, Union

import torch
import torch.nn as nn
from mmengine.model import ModuleList

from mmocr.models.common import PositionalEncoding, TFDecoderLayer, Cached_TFDecoderLayer
from mmocr.models.common.dictionary import Dictionary
from mmocr.registry import MODELS
from mmocr.structures import TextRecogDataSample
from .base import BaseDecoder


@MODELS.register_module()
class NRTRDecoder(BaseDecoder):
    """Transformer Decoder block with self attention mechanism.

    Args:
        n_layers (int): Number of attention layers. Defaults to 6.
        d_embedding (int): Language embedding dimension. Defaults to 512.
        n_head (int): Number of parallel attention heads. Defaults to 8.
        d_k (int): Dimension of the key vector. Defaults to 64.
        d_v (int): Dimension of the value vector. Defaults to 64
        d_model (int): Dimension :math:`D_m` of the input from previous model.
            Defaults to 512.
        d_inner (int): Hidden dimension of feedforward layers. Defaults to 256.
        n_position (int): Length of the positional encoding vector. Must be
            greater than ``max_seq_len``. Defaults to 200.
        dropout (float): Dropout rate for text embedding, MHSA, FFN. Defaults
            to 0.1.
        module_loss (dict, optional): Config to build module_loss. Defaults
            to None.
        postprocessor (dict, optional): Config to build postprocessor.
            Defaults to None.
        dictionary (dict or :obj:`Dictionary`): The config for `Dictionary` or
            the instance of `Dictionary`.
        max_seq_len (int): Maximum output sequence length :math:`T`. Defaults
            to 30.
        init_cfg (dict or list[dict], optional): Initialization configs.
    """

    def __init__(self,
                 n_layers: int = 6,
                 d_embedding: int = 512,
                 n_head=8,
                 d_k: int = 64,
                 d_v: int = 64,
                 d_model: int = 512,
                 d_inner=256,
                 d_enc=-1,
                 n_position: int = 200,
                 dropout: float = 0.1,
                 module_loss: Optional[Dict] = None,
                 postprocessor: Optional[Dict] = None,
                 dictionary: Optional[Union[Dict, Dictionary]] = None,
                 max_seq_len: int = 30,
                 init_cfg: Optional[Union[Dict, List[Dict]]] = None,
                 caching=False
                 ) -> None:
        super().__init__(
            module_loss=module_loss,
            postprocessor=postprocessor,
            dictionary=dictionary,
            init_cfg=init_cfg,
            max_seq_len=max_seq_len)

        self.padding_idx = self.dictionary.padding_idx
        self.start_idx = self.dictionary.start_idx
        self.max_seq_len = max_seq_len

        # added for caching
        self.caching = caching

        self.trg_word_emb = nn.Embedding(
            self.dictionary.num_classes,
            d_embedding,
            padding_idx=self.padding_idx)

        self.position_enc = PositionalEncoding(d_embedding, n_position=n_position, caching=self.caching)
        self.dropout = nn.Dropout(p=dropout)

        self.layer_stack = []
        pred_num_class = self.dictionary.num_classes
        if isinstance(n_head, dict) and isinstance(d_inner, list):
            for i in range(n_layers):
                if self.caching:
                    self.layer_stack.append(Cached_TFDecoderLayer(
                        d_model, d_inner[i], (n_head['self'][i], n_head['cross'][i]), d_k, d_v, dropout=dropout,
                        d_embedding=d_embedding, d_enc=d_enc))
                else:
                    self.layer_stack.append(
                        TFDecoderLayer(d_model, d_inner[i], (n_head['self'][i], n_head['cross'][i]), d_k, d_v,
                                       dropout=dropout, d_embedding=d_embedding, d_enc=d_enc))
            self.layer_stack = ModuleList(self.layer_stack)
            self.layer_norm = nn.LayerNorm(d_embedding, eps=1e-6)
            self.classifier = nn.Linear(d_embedding, pred_num_class)
        else:
            for _ in range(n_layers):
                if self.caching:
                    self.layer_stack.append(Cached_TFDecoderLayer(d_model, d_inner, n_head, d_k, d_v, dropout=dropout))
                else:
                    self.layer_stack.append(TFDecoderLayer(d_model, d_inner, n_head, d_k, d_v, dropout=dropout))
            self.layer_stack = ModuleList(self.layer_stack)
            self.layer_norm = nn.LayerNorm(d_model, eps=1e-6)
            self.classifier = nn.Linear(d_model, pred_num_class)

        # self.layer_stack = ModuleList([
        #     TFDecoderLayer(
        #         d_model, d_inner, n_head, d_k, d_v, dropout=dropout) if not self.caching \
        #     else Cached_TFDecoderLayer(d_model, d_inner, n_head, d_k, d_v, dropout=dropout)
        #             # modified by YJ

        #     # TFDecoderLayer(
        #     #     d_model, d_inner, n_head, d_k, d_v, dropout=dropout)
        #     for _ in range(n_layers)
        # ])

        self.softmax = nn.Softmax(dim=-1)

    def _get_target_mask(self, trg_seq: torch.Tensor) -> torch.Tensor:
        """Generate mask for target sequence.

        Args:
            trg_seq (torch.Tensor): Input text sequence. Shape :math:`(N, T)`.

        Returns:
            Tensor: Target mask. Shape :math:`(N, T, T)`.
            E.g.:
            seq = torch.Tensor([[1, 2, 0, 0]]), pad_idx = 0, then
            target_mask =
            torch.Tensor([[[True, False, False, False],
            [True, True, False, False],
            [True, True, False, False],
            [True, True, False, False]]])
        """

        pad_mask = (trg_seq != self.padding_idx).unsqueeze(-2)

        len_s = trg_seq.size(1)
        subsequent_mask = 1 - torch.triu(
            torch.ones((len_s, len_s), device=trg_seq.device), diagonal=1)
        subsequent_mask = subsequent_mask.unsqueeze(0).bool()

        return pad_mask & subsequent_mask

    def _get_source_mask(self, src_seq: torch.Tensor,
                         valid_ratios: Sequence[float]) -> torch.Tensor:
        """Generate mask for source sequence.

        Args:
            src_seq (torch.Tensor): Image sequence. Shape :math:`(N, T, C)`.
            valid_ratios (list[float]): The valid ratio of input image. For
                example, if the width of the original image is w1 and the width
                after padding is w2, then valid_ratio = w1/w2. Source mask is
                used to cover the area of the padding region.

        Returns:
            Tensor or None: Source mask. Shape :math:`(N, T)`. The region of
            padding area are False, and the rest are True.
        """

        N, T, _ = src_seq.size()
        mask = None
        if len(valid_ratios) > 0:
            mask = src_seq.new_zeros((N, T), device=src_seq.device)
            for i, valid_ratio in enumerate(valid_ratios):
                valid_width = min(T, math.ceil(T * valid_ratio))
                mask[i, :valid_width] = 1

        return mask

    def _attention(self,
                   trg_seq: torch.Tensor,
                   src: torch.Tensor,
                   src_mask: Optional[torch.Tensor] = None,
                   cache: Optional[torch.Tensor] = None,  # added
                   ) -> torch.Tensor:
        """A wrapped process for transformer based decoder including text
        embedding, position embedding, N x transformer decoder and a LayerNorm
        operation.

        Args:
            trg_seq (Tensor): Target sequence in. Shape :math:`(N, T)`.
            src (Tensor): Source sequence from encoder in shape
                Shape :math:`(N, T, D_m)` where :math:`D_m` is ``d_model``.
            src_mask (Tensor, Optional): Mask for source sequence.
                Shape :math:`(N, T)`. Defaults to None.

        Returns:
            Tensor: Output sequence from transformer decoder.
            Shape :math:`(N, T, D_m)` where :math:`D_m` is ``d_model``.
        """
        if self.training:
            if cache is not None:
                raise ValueError("cache parameter should be None in training mode")

        # cum_len = 0
        # if self.caching:
        #     cum_len = trg_seq.shape[1]
        #     trg_seq = trg_seq[:, -1:]

        trg_embedding = self.trg_word_emb(trg_seq)
        trg_pos_encoded = self.position_enc(trg_embedding)
        # trg_pos_encoded = self.position_enc(trg_embedding, cum_len, cache != None)
        trg_mask = self._get_target_mask(trg_seq)
        tgt_seq = self.dropout(trg_pos_encoded)

        output = tgt_seq

        # added for caching
        new_decoder_cache = []
        # new_cache = None

        for i, dec_layer in enumerate(self.layer_stack):
            # for dec_layer in self.layer_stack:
            if self.caching:
                cache_i = cache[i] if cache is not None else None
                output, updated_cache = dec_layer(
                    output,
                    src,
                    self_attn_mask=trg_mask,
                    dec_enc_attn_mask=src_mask,
                    cache=cache_i)

                new_decoder_cache.append(updated_cache.copy())
            else:
                output = dec_layer(
                    output,
                    src,
                    self_attn_mask=trg_mask,
                    dec_enc_attn_mask=src_mask, )

            if i == len(self.layer_stack) - 1:
                output = self.layer_norm(output)

        # output = self.layer_norm(output)
        if len(new_decoder_cache):
            return output, new_decoder_cache

        return output

    def forward_train(self,
                      feat: Optional[torch.Tensor] = None,
                      out_enc: torch.Tensor = None,
                      data_samples: Sequence[TextRecogDataSample] = None
                      ) -> torch.Tensor:
        """Forward for training. Source mask will be used here.

        Args:
            feat (Tensor, optional): Unused.
            out_enc (Tensor): Encoder output of shape : math:`(N, T, D_m)`
                where :math:`D_m` is ``d_model``. Defaults to None.
            data_samples (list[TextRecogDataSample]): Batch of
                TextRecogDataSample, containing gt_text and valid_ratio
                information. Defaults to None.

        Returns:
            Tensor: The raw logit tensor. Shape :math:`(N, T, C)` where
            :math:`C` is ``num_classes``.
        """
        valid_ratios = []
        for data_sample in data_samples:
            valid_ratios.append(data_sample.get('valid_ratio'))
        src_mask = self._get_source_mask(out_enc, valid_ratios)
        trg_seq = []
        for data_sample in data_samples:
            trg_seq.append(
                data_sample.gt_text.padded_indexes.to(out_enc.device))
        trg_seq = torch.stack(trg_seq, dim=0)
        attn_output = self._attention(trg_seq, out_enc, src_mask=src_mask)
        outputs = self.classifier(attn_output)

        return outputs

    def forward_test(self,
                     feat: Optional[torch.Tensor] = None,
                     out_enc: torch.Tensor = None,
                     data_samples: Sequence[TextRecogDataSample] = None,
                     cache: Optional[torch.Tensor] = None,  # added
                     ) -> torch.Tensor:
        """Forward for testing.

        Args:
            feat (Tensor, optional): Unused.
            out_enc (Tensor): Encoder output of shape:
                math:`(N, T, D_m)` where :math:`D_m` is ``d_model``.
                Defaults to None.
            data_samples (list[TextRecogDataSample]): Batch of
                TextRecogDataSample, containing gt_text and valid_ratio
                information. Defaults to None.

        Returns:
            Tensor: Character probabilities. of shape
            :math:`(N, self.max_seq_len, C)` where :math:`C` is
            ``num_classes``.
        """
        valid_ratios = []
        if data_samples is not None:
            for data_sample in data_samples:
                valid_ratios.append(data_sample.get('valid_ratio'))
            src_mask = self._get_source_mask(out_enc, valid_ratios)
        else:
            src_mask = torch.ones((out_enc.shape[0], out_enc.shape[1]), device=out_enc.device)
        N = out_enc.size(0)

        init_target_seq = torch.full((N, self.max_seq_len + 1),
                                     self.padding_idx,
                                     device=out_enc.device,
                                     dtype=torch.long)
        # bsz * seq_len
        init_target_seq[:, 0] = self.start_idx

        if self.caching:
            init_target_seq = init_target_seq[:, :1]  # only use start token

        outputs = []

        for step in range(0, self.max_seq_len):
            if self.caching:
                decoder_output, cache = self._attention(
                    init_target_seq, out_enc, src_mask=src_mask, cache=cache)  # add cache
            else:
                decoder_output = self._attention(
                    init_target_seq, out_enc, src_mask=src_mask)
            # bsz * seq_len * C
            if self.caching:
                step_result = self.classifier(decoder_output[:, -1, :])
            else:
                step_result = self.classifier(decoder_output[:, step, :])
            # bsz * num_classes
            outputs.append(step_result)
            _, step_max_index = torch.max(step_result, dim=-1)
            if self.caching:
                init_target_seq = torch.cat(
                    [init_target_seq, step_max_index[:, None]], dim=1
                )
            else:
                init_target_seq[:, step + 1] = step_max_index

        outputs = torch.stack(outputs, dim=1)

        return self.softmax(outputs)
