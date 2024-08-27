# Copyright (c) OpenMMLab. All rights reserved.
import os
import warnings
import numpy as np
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Optional, Union

import torch

from mmocr.apis.inferencers import MMOCRInferencer
from mmocr.apis.inferencers.base_mmocr_inferencer import InputsType
from mmocr.utils import register_all_modules

import cv2


def gap_with_pad_width(image, desired_width) -> np.array:
    """Maintains aspect ratio and resizes with padding.
    Params:
        image: Image to be resized.
        new_shape: Expected (width, height) of new image.
        padding_color: Tuple in BGR of padding color
    Returns:
        image: Resized image with padding
    """

    # print(f"new_size width :{image.shape[1]}, heights :{image.shape[0]}")
    origin_w = image.shape[1]

    if origin_w > desired_width:
        new_img = image_resize(image, width=desired_width)
        return new_img
    else:
        delta_w = desired_width-origin_w
        left, right = delta_w // 2, delta_w - (delta_w // 2)
        top, bottom = 0, 0
        padding_color = (255,255,255)
        new_img = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)

        return new_img


def gap_with_pad_height(image, desired_height) -> np.array:
    """Maintains aspect ratio and resizes with padding.
    Params:
        image: Image to be resized.
        new_shape: Expected (width, height) of new image.
        padding_color: Tuple in BGR of padding color
    Returns:
        image: Resized image with padding
    """

    # print(f"new_size width :{image.shape[1]}, heights :{image.shape[0]}")
    origin_h = image.shape[0]

    if origin_h > desired_height:
        new_img = image_resize(image, height=desired_height)
        return new_img
    else:
        delta_h = desired_height-origin_h
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = 0, 0
        padding_color = (255,255,255)
        new_img = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)

        return new_img
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '--img', type=str, help='Input image file or folder path.')
    parser.add_argument(
        '--img-out-dir',
        type=str,
        default='',
        help='Output directory of images.')
    parser.add_argument(
        '--det',
        type=str,
        default=None,
        help='Pretrained text detection algorithm')
    parser.add_argument(
        '--det-config',
        type=str,
        default=None,
        help='Path to the custom config file of the selected det model. It '
        'overrides the settings in det')
    parser.add_argument(
        '--det-ckpt',
        type=str,
        default=None,
        help='Path to the custom checkpoint file of the selected det model. '
        'It overrides the settings in det')
    parser.add_argument(
        '--recog',
        type=str,
        default=None,
        help='Pretrained text recognition algorithm')
    parser.add_argument(
        '--recog-config',
        type=str,
        default=None,
        help='Path to the custom config file of the selected recog model. It'
        'overrides the settings in recog')
    parser.add_argument(
        '--recog-ckpt',
        type=str,
        default=None,
        help='Path to the custom checkpoint file of the selected recog model. '
        'It overrides the settings in recog')
    parser.add_argument(
        '--kie',
        type=str,
        default=None,
        help='Pretrained key information extraction algorithm')
    parser.add_argument(
        '--kie-config',
        type=str,
        default=None,
        help='Path to the custom config file of the selected kie model. It'
        'overrides the settings in kie')
    parser.add_argument(
        '--kie-ckpt',
        type=str,
        default=None,
        help='Path to the custom checkpoint file of the selected kie model. '
        'It overrides the settings in kie')
    parser.add_argument(
        '--config-dir',
        type=str,
        default=os.path.join(str(Path.cwd()), 'configs/'),
        help='Path to the config directory where all the config files '
        'are located. Defaults to "configs/"')
    parser.add_argument(
        '--device',
        type=str,
        default='cuda',
        help='Device used for inference.')
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display the image in a popup window.')
    parser.add_argument(
        '--print-result',
        action='store_true',
        help='Whether to print the results.')
    parser.add_argument(
        '--pred-out-file',
        type=str,
        default='',
        help='File to save the inference results.')

    args = parser.parse_args()
    # Warnings
    if not os.path.samefile(args.config_dir, os.path.join(str(
            Path.cwd()))) and (args.det_config != ''
                               or args.recog_config != ''):
        warnings.warn(
            'config_dir will be overridden by det-config or recog-config.',
            UserWarning)
    return args


class MMOCR:
    """MMOCR API for text detection, recognition, KIE inference.

    Args:
        det (str): Name of the detection model. Default to 'FCE_IC15'.
        det_config (str): Path to the config file for the detection model.
            Default to None.
        det_ckpt (str): Path to the checkpoint file for the detection model.
            Default to None.
        recog (str): Name of the recognition model. Default to 'CRNN'.
        recog_config (str): Path to the config file for the recognition model.
            Default to None.
        recog_ckpt (str): Path to the checkpoint file for the recognition
            model. Default to None.
        kie (str): Name of the KIE model. Default to None.
        kie_config (str): Path to the config file for the KIE model. Default
            to None.
        kie_ckpt (str): Path to the checkpoint file for the KIE model.
            Default to None.
        config_dir (str): Path to the directory containing config files.
            Default to 'configs/'.
        device (torch.device): Device to use for inference. Default to 'cuda'.
    """

    def __init__(self,
                 det: str = None,
                 det_config: str = None,
                 det_ckpt: str = None,
                 recog: str = None,
                 recog_config: str = None,
                 recog_ckpt: str = None,
                 kie: str = None,
                 kie_config: str = None,
                 kie_ckpt: str = None,
                 config_dir: str = os.path.join(str(Path.cwd()), 'configs/'),
                 device: torch.device = 'cuda',
                 **kwargs) -> None:

        register_all_modules(init_default_scope=True)

        self.config_dir = config_dir
        inferencer_kwargs = {}
        inferencer_kwargs.update(
            self._get_inferencer_kwargs(det, det_config, det_ckpt, 'det_'))
        inferencer_kwargs.update(
            self._get_inferencer_kwargs(recog, recog_config, recog_ckpt,
                                        'rec_'))
        inferencer_kwargs.update(
            self._get_inferencer_kwargs(kie, kie_config, kie_ckpt, 'kie_'))
        self.inferencer = MMOCRInferencer(device=device, **inferencer_kwargs)

    def _get_inferencer_kwargs(self, model: Optional[str],
                               config: Optional[str], ckpt: Optional[str],
                               prefix: str) -> Dict:
        """Get the kwargs for the inferencer."""
        kwargs = {}

        if model is not None:
            cfgs = self.get_model_config(model)
            kwargs[prefix + 'config'] = os.path.join(self.config_dir,
                                                     cfgs['config'])
            kwargs[prefix + 'ckpt'] = 'https://download.openmmlab.com/' + \
                f'mmocr/{cfgs["ckpt"]}'

        if config is not None:
            if kwargs.get(prefix + 'config', None) is not None:
                warnings.warn(
                    f'{model}\'s default config is overridden by {config}',
                    UserWarning)
            kwargs[prefix + 'config'] = config

        if ckpt is not None:
            if kwargs.get(prefix + 'ckpt', None) is not None:
                warnings.warn(
                    f'{model}\'s default checkpoint is overridden by {ckpt}',
                    UserWarning)
            kwargs[prefix + 'ckpt'] = ckpt
        return kwargs

    def readtext(self,
                 img: InputsType,
                 img_out_dir: str = '',
                 show: bool = False,
                 print_result: bool = False,
                 pred_out_file: str = '',
                 **kwargs) -> Union[Dict, List[Dict]]:
        """Inferences text detection, recognition, and KIE on an image or a
        folder of images.

        Args:
            imgs (str or np.array or Sequence[str or np.array]): Img,
                folder path, np array or list/tuple (with img
                paths or np arrays).
            img_out_dir (str): Output directory of images. Defaults to ''.
            show (bool): Whether to display the image in a popup window.
                Defaults to False.
            print_result (bool): Whether to print the results.
            pred_out_file (str): File to save the inference results. If left as
                empty, no file will be saved.

        Returns:
            Dict or List[Dict]: Each dict contains the inference result of
            each image. Possible keys are "det_polygons", "det_scores",
            "rec_texts", "rec_scores", "kie_labels", "kie_scores",
            "kie_edge_labels" and "kie_edge_scores".
        """

        idx = img.rfind("/")
        prefix = img[:idx]
        print("prefix:", prefix)
        files = os.listdir(img)
        for file in files:
            print("full path :", prefix+"/"+file)
            img = prefix+"/"+file

            img_np = cv2.imread(img)

            crop_w = img_np.shape[1]
            crop_h = img_np.shape[0]

            if (crop_w > 0) and (crop_h > 0):

                if crop_h >= crop_w * 2:  # 세로 글씨

                    # step 1.
                    img = image_resize(img_np, height=100)

                    # step 2. 패딩
                    desired_width = 32
                    new_img = gap_with_pad_width(img, desired_width)

                    # step 3. 100으로 리사이즈 하면 32보다 작은 경우 남는 공간 패딩
                    desired_height = 100
                    new_img = gap_with_pad_height(new_img, desired_height)

                else:
                    # step 1.
                    img = image_resize(img_np, height=32)
                    print("img :", img.shape)

                    # step 2. 패딩
                    desired_width = 100
                    new_img = gap_with_pad_width(img, desired_width)

                    # step 3. 100으로 리사이즈 하면 32보다 작은 경우 남는 공간 패딩
                    desired_height = 32
                    new_img = gap_with_pad_height(new_img, desired_height)

                self.inferencer(
                    new_img,
                    img_out_dir=img_out_dir,
                    show=show,
                    print_result=print_result,
                    pred_out_file=pred_out_file)

        return 0

            # return self.inferencer(
            #     img,
            #     img_out_dir=img_out_dir,
            #     show=show,
            #     print_result=print_result,
            #     pred_out_file=pred_out_file)

    def get_model_config(self, model_name: str) -> Dict:
        """Get the model configuration including model config and checkpoint
        url.

        Args:
            model_name (str): Name of the model.
        Returns:
            dict: Model configuration.
        """
        model_dict = {
            'Tesseract': {},
            # Detection models
            'DB_r18': {
                'config':
                'textdet/'
                'dbnet/dbnet_resnet18_fpnc_1200e_icdar2015.py',
                'ckpt':
                'textdet/'
                'dbnet/'
                'dbnet_resnet18_fpnc_1200e_icdar2015/'
                'dbnet_resnet18_fpnc_1200e_icdar2015_20220825_221614-7c0e94f2.pth'  # noqa: E501
            },
            'DB_r50': {
                'config':
                'textdet/'
                'dbnet/dbnet_resnet50-dcnv2_fpnc_1200e_icdar2015.py',
                'ckpt':
                'textdet/'
                'dbnet/'
                'dbnet_resnet50-dcnv2_fpnc_1200e_icdar2015'
                'dbnet_resnet50-dcnv2_fpnc_1200e_icdar2015_20220828_124917-452c443c.pth'  # noqa: E501
            },
            'DBPP_r50': {
                'config':
                'textdet/'
                'dbnetpp/dbnetpp_resnet50-dcnv2_fpnc_1200e_icdar2015.py',
                'ckpt':
                'detection_KT_v1.0.0_240726_release.pth'  # noqa: E501
            },
            'DRRG': {
                'config':
                'textdet/'
                'drrg/drrg_resnet50_fpn-unet_1200e_ctw1500.py',
                'ckpt':
                'textdet/'
                'drrg/'
                'drrg_resnet50_fpn-unet_1200e_ctw1500/'
                'drrg_resnet50_fpn-unet_1200e_ctw1500_20220827_105233-d5c702dd.pth'  # noqa: E501
            },
            'FCE_IC15': {
                'config':
                'textdet/'
                'fcenet/fcenet_resnet50_fpn_1500e_icdar2015.py',
                'ckpt':
                'textdet/'
                'fcenet/'
                'fcenet_resnet50_fpn_1500e_icdar2015/'
                'fcenet_resnet50_fpn_1500e_icdar2015_20220826_140941-167d9042.pth'  # noqa: E501
            },
            'FCE_CTW_DCNv2': {
                'config':
                'textdet/'
                'fcenet/fcenet_resnet50-dcnv2_fpn_1500e_ctw1500.py',
                'ckpt':
                'textdet/'
                'fcenet/'
                'fcenet_resnet50-dcnv2_fpn_1500e_ctw1500/'
                'fcenet_resnet50-dcnv2_fpn_1500e_ctw1500_20220825_221510-4d705392.pth'  # noqa: E501
            },
            'MaskRCNN_CTW': {
                'config':
                'textdet/'
                'maskrcnn/mask-rcnn_resnet50_fpn_160e_ctw1500.py',
                'ckpt':
                'textdet/'
                'maskrcnn/'
                'mask-rcnn_resnet50_fpn_160e_ctw1500/'
                'mask-rcnn_resnet50_fpn_160e_ctw1500_20220826_154755-ce68ee8e.pth'  # noqa: E501
            },
            'MaskRCNN_IC15': {
                'config':
                'textdet/'
                'maskrcnn/mask-rcnn_resnet50_fpn_160e_icdar2015.py',
                'ckpt':
                'textdet/'
                'maskrcnn/'
                'mask-rcnn_resnet50_fpn_160e_icdar2015/'
                'mask-rcnn_resnet50_fpn_160e_icdar2015_20220826_154808-ff5c30bf.pth'  # noqa: E501
            },
            # 'MaskRCNN_IC17': {
            #     'config':
            #     'textdet/'
            #     'maskrcnn/mask-rcnn_resnet50_fpn_160e_icdar2017.py',
            #     'ckpt':
            #     'textdet/'
            #     'maskrcnn/'
            #     ''
            # },
            'PANet_CTW': {
                'config':
                'textdet/'
                'panet/panet_resnet18_fpem-ffm_600e_ctw1500.py',
                'ckpt':
                'textdet/'
                'panet/'
                'panet_resnet18_fpem-ffm_600e_ctw1500/'
                'panet_resnet18_fpem-ffm_600e_ctw1500_20220826_144818-980f32d0.pth'  # noqa: E501
            },
            'PANet_IC15': {
                'config':
                'textdet/'
                'panet/panet_resnet18_fpem-ffm_600e_icdar2015.py',
                'ckpt':
                'textdet/'
                'panet/'
                'panet_resnet18_fpem-ffm_600e_icdar2015/'
                'panet_resnet18_fpem-ffm_600e_icdar2015_20220826_144817-be2acdb4.pth'  # noqa: E501
            },
            'PS_CTW': {
                'config':
                'textdet/'
                'psenet/psenet_resnet50_fpnf_600e_ctw1500.py',
                'ckpt':
                'textdet/'
                'psenet/'
                'psenet_resnet50_fpnf_600e_ctw1500/'
                'psenet_resnet50_fpnf_600e_ctw1500_20220825_221459-7f974ac8.pth'  # noqa: E501
            },
            'PS_IC15': {
                'config':
                'textdet/'
                'psenet/psenet_resnet50_fpnf_600e_icdar2015.py',
                'ckpt':
                'textdet/'
                'psenet/'
                'psenet_resnet50_fpnf_600e_icdar2015/'
                'psenet_resnet50_fpnf_600e_icdar2015_20220825_222709-b6741ec3.pth'  # noqa: E501
            },
            'TextSnake': {
                'config':
                'textdet/'
                'textsnake/textsnake_resnet50_fpn-unet_1200e_ctw1500.py',
                'ckpt':
                'textdet/'
                'textsnake/'
                'textsnake_resnet50_fpn-unet_1200e_ctw1500/'
                'textsnake_resnet50_fpn-unet_1200e_ctw1500_20220825_221459-c0b6adc4.pth'  # noqa: E501
            },
            # Recognition models
            'CRNN': {
                'config':
                'textrecog/crnn/crnn_mini-vgg_5e_mj.py',
                'ckpt':
                'textrecog/crnn/crnn_mini-vgg_5e_mj/crnn_mini-vgg_5e_mj_20220826_224120-8afbedbb.pth'  # noqa: E501
            },
            'SAR': {
                'config':
                'textrecog/sar/'
                'sar_resnet31_parallel-decoder_5e_st-sub_mj-sub_sa_real.py',
                'ckpt':
                'textrecog/sar/sar_resnet31_parallel-decoder_5e_st-sub_mj-sub_sa_real/sar_resnet31_parallel-decoder_5e_st-sub_mj-sub_sa_real_20220915_171910-04eb4e75.pth'  # noqa: E501
            },
            # 'SAR_CN': {
            #     'config':
            #     'textrecog/'
            #     'sar/sar_r31_parallel_decoder_chinese.py',
            #     'ckpt':
            #     'textrecog/'  # noqa: E501
            #     ''
            # },
            'NRTR_1/16-1/8': {
                'config':
                'textrecog/'
                'nrtr/nrtr_resnet31-1by16-1by8_6e_st_mj.py',
                'ckpt':
                'textrecog/'
                'nrtr/nrtr_resnet31-1by16-1by8_6e_st_mj/nrtr_resnet31-1by16-1by8_6e_st_mj_20220920_143358-43767036.pth'  # noqa: E501
            },
            'NRTR_1/8-1/4': {
                'config':
                'textrecog/'
                'nrtr/nrtr_resnet31-1by8-1by4_6e_st_mj.py',
                'ckpt':
                'textrecog/'
                'nrtr/nrtr_resnet31-1by8-1by4_6e_st_mj/nrtr_resnet31-1by8-1by4_6e_st_mj_20220916_103322-a6a2a123.pth'  # noqa: E501
            },
            'RobustScanner': {
                'config':
                'textrecog/robust_scanner/'
                'robustscanner_resnet31_5e_st-sub_mj-sub_sa_real.py',
                'ckpt':
                'textrecog/'
                'robust_scanner/robustscanner_resnet31_5e_st-sub_mj-sub_sa_real/robustscanner_resnet31_5e_st-sub_mj-sub_sa_real_20220915_152447-7fc35929.pth'  # noqa: E501
            },
            'SATRN': {
                'config':
                'textrecog/satrn/satrn_shallow_5e_st_mj.py',
                'ckpt':
                'recognition_KT_v1.0.0_240726_release.pth'  # noqa: E501
            },
            'SATRN_sm': {
                'config':
                'textrecog/satrn/satrn_shallow-small_5e_st_mj.py',
                'ckpt':
                'textrecog/'
                'satrn/satrn_shallow-small_5e_st_mj/satrn_shallow-small_5e_st_mj_20220915_152442-5591bf27.pth'  # noqa: E501
            },
            'ABINet': {
                'config':
                'textrecog/abinet/abinet_20e_st-an_mj.py',
                'ckpt':
                'textrecog/'
                'abinet/abinet_20e_st-an_mj/abinet_20e_st-an_mj_20221005_012617-ead8c139.pth'  # noqa: E501
            },
            'ABINet_Vision': {
                'config':
                'textrecog/abinet/abinet-vision_20e_st-an_mj.py',
                'ckpt':
                'textrecog/'
                'abinet/abinet-vision_20e_st-an_mj/abinet-vision_20e_st-an_mj_20220915_152445-85cfb03d.pth'  # noqa: E501
            },
            # 'CRNN_TPS': {
            #     'config':
            #     'textrecog/tps/crnn_tps_academic_dataset.py',
            #     'ckpt':
            #     'textrecog/'
            #     ''
            # },
            'MASTER': {
                'config':
                'textrecog/master/master_resnet31_12e_st_mj_sa.py',
                'ckpt':
                'textrecog/'
                'master/master_resnet31_12e_st_mj_sa/master_resnet31_12e_st_mj_sa_20220915_152443-f4a5cabc.pth'  # noqa: E501
            },
            'ASTER': {
                'config':
                'textrecog/aster/aster_resnet45_6e_st_mj.py',
                'ckpt':
                'textrecog/'
                'aster/aster_resnet45_6e_st_mj/aster_resnet45_6e_st_mj-cc56eca4.pth'  # noqa: E501
            },
            # KIE models
            'SDMGR': {
                'config':
                'kie/sdmgr/sdmgr_unet16_60e_wildreceipt.py',
                'ckpt':
                'kie/'
                'sdmgr/'
                'sdmgr_unet16_60e_wildreceipt/'
                'sdmgr_unet16_60e_wildreceipt_20220825_151648-22419f37.pth'
            }
        }
        if model_name not in model_dict:
            raise ValueError(f'Model {model_name} is not supported.')
        else:
            return model_dict[model_name]


def main():
    args = parse_args()
    ocr = MMOCR(**vars(args))
    ocr.readtext(**vars(args))


if __name__ == '__main__':
    main()