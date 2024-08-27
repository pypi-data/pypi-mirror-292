# Copyright (c) OpenMMLab. All rights reserved.
import json
from pathlib import Path
import os
import torch
from argparse import ArgumentParser
from typing import Dict, List, Optional, Union
import cv2
from mmocr.apis.inferencers import MMOCRInferencer
from mmocr.apis.inferencers.mmocr_inferencer_batch import MMOCRBatchInferencer
from mmocr.utils import register_all_modules
import warnings
import numpy as np


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '--inputs', type=str, help='Input image file or folder path.')
    parser.add_argument(
        '--out-dir',
        type=str,
        default='results/',
        help='Output directory of results.')
    parser.add_argument(
        '--det',
        type=str,
        default='SATRN',
        help='Pretrained text detection algorithm. It\'s the path to the '
             'config file or the model name defined in metafile.')
    parser.add_argument(
        '--det-weights',
        type=str,
        default='detection_KT_v1.0.0_240726_release.pth',
        help='Path to the custom checkpoint file of the selected det model. '
             'If it is not specified and "det" is a model name of metafile, the '
             'weights will be loaded from metafile.')
    parser.add_argument(
        '--rec',
        type=str,
        default='DBPP_r50',
        help='Pretrained text recognition algorithm. It\'s the path to the '
             'config file or the model name defined in metafile.')
    parser.add_argument(
        '--rec-weights',
        type=str,
        default='recognition_KT_v1.0.0_240726_release.pth',
        help='Path to the custom checkpoint file of the selected recog model. '
             'If it is not specified and "rec" is a model name of metafile, the '
             'weights will be loaded from metafile.')
    parser.add_argument(
        '--kie',
        type=str,
        default=None,
        help='Pretrained key information extraction algorithm. It\'s the path'
             'to the config file or the model name defined in metafile.')
    parser.add_argument(
        '--kie-weights',
        type=str,
        default=None,
        help='Path to the custom checkpoint file of the selected kie model. '
             'If it is not specified and "kie" is a model name of metafile, the '
             'weights will be loaded from metafile.')
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        help='Device used for inference. '
             'If not specified, the available device will be automatically used.')
    parser.add_argument(
        '--batch-size', type=int, default=1, help='Inference batch size.')
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display the image in a popup window.')
    parser.add_argument(
        '--print-result',
        action='store_true',
        help='Whether to print the results.')
    parser.add_argument(
        '--save_pred',
        action='store_true',
        help='Save the inference results to out_dir.')
    parser.add_argument(
        '--save_vis',
        action='store_true',
        help='Save the visualization results to out_dir.')

    call_args = vars(parser.parse_args())

    init_kws = [
        'det', 'det_weights', 'rec', 'rec_weights', 'kie', 'kie_weights',
        'device'
    ]
    init_args = {}
    for init_kw in init_kws:
        init_args[init_kw] = call_args.pop(init_kw)

    return init_args, call_args


def convert_to_bounding_box(coordinates):
    x_values = coordinates[::2]  # 짝수 인덱스는 x 좌표
    y_values = coordinates[1::2]  # 홀수 인덱스는 y 좌표
    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)
    return min_x, min_y, max_x, max_y


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # original image
    if width is None and height is None:
        return image, 1

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
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized, r


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
        new_img, scale = image_resize(image, width=desired_width)
        return new_img
    else:
        delta_w = desired_width - origin_w
        left, right = delta_w // 2, delta_w - (delta_w // 2)
        top, bottom = 0, 0
        padding_color = (255, 255, 255)
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
        return new_img, 0, 0
    else:
        delta_h = desired_height - origin_h
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = 0, 0
        padding_color = (255, 255, 255)
        new_img = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)

        return new_img, top, bottom


def rescale_bounding_boxes(original_img, resized_img, bounding_boxes, scale_w, pad_top):
    rescaled_boxes = []
    for (x, y, w, h) in bounding_boxes:
        rescaled_x = int(x / scale_w)
        rescaled_y = int((y - pad_top) / scale_w)
        rescaled_w = int(w / scale_w)
        rescaled_h = int(h / scale_w)
        rescaled_boxes.append([rescaled_x, rescaled_y, rescaled_w, rescaled_h])

    return rescaled_boxes

# Rescale function for bounding boxes
def rsz_rescale_bounding_boxes(original_img, resized_img, bounding_boxes):
    (orig_h, orig_w) = original_img.shape[:2]
    (resized_h, resized_w) = resized_img.shape[:2]

    scale_w = orig_w / float(resized_w)
    scale_h = orig_h / float(resized_h)

    rescaled_boxes = []
    for (x, y, w, h) in bounding_boxes:
        rescaled_x = int(x * scale_w)
        rescaled_y = int(y * scale_h)
        rescaled_w = int(w * scale_w)
        rescaled_h = int(h * scale_h)
        rescaled_boxes.append([rescaled_x, rescaled_y, rescaled_w, rescaled_h])

    return rescaled_boxes

def run_ocr(test_image, det, det_weights, rec, rec_weights):
    init_args, call_args = parse_args()
    call_args['inputs'] = test_image
    init_args['det'] = det
    init_args['rec'] = rec
    init_args['det_weights'] = det_weights
    init_args['rec_weights'] = rec_weights

    cv_img = cv2.imread(test_image)
    height, width, _ = cv_img.shape

    width_is_longer = (width >= height)
    if width_is_longer:
        new_img, scale = image_resize(cv_img, width=2560)
        desired_height = 2560
        new_img, top, bottom = gap_with_pad_height(new_img, desired_height)
        padding_size, h_padding_size = 4, 2
    else:
        new_img, scale = image_resize(cv_img, height=3000)
        padding_size, h_padding_size = 3, 1

    call_args['inputs'] = new_img
    ocr = MMOCRInferencer(**init_args)
    result = ocr(**call_args)['predictions'][0]  # RETURNS: res['predictions'], res['visualization']

    results = []
    filtered_polygons = []
    for i, score in enumerate(result["det_scores"]):
        if score >= 0.4:
            filtered_polygons.append(result["det_polygons"][i])

    # 각 다각형에 대해 바운딩 박스 좌표로 변환
    bounding_boxes = [convert_to_bounding_box(coords) for coords in filtered_polygons]

    for i, bbox in enumerate(bounding_boxes, start=1):
        x, y, x2, y2 = bbox
        ## for padding ##
        x, y, x2, y2 = x - padding_size, y - h_padding_size, x2 + padding_size + 2, y2 + h_padding_size + 3
        w, h = x2 - x, y2 - y
        if not width_is_longer:
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if w < 0:
                w = 0
            if h < 0:
                h = 0
        results.append([int(x), int(y), int(w), int(h)])

    if width_is_longer:
        rescaled_boxes = rescale_bounding_boxes(cv_img, new_img, results, scale, top)
    else:
        rescaled_boxes = rsz_rescale_bounding_boxes(cv_img, new_img, results)

    # text_det_bboxes = {
    #     "allbboxes": results,
    #     "origin-allbboxes": rescaled_boxes
    # }

    # OCR - RECOGNITION PART ------------------------------------------- #
    text_list = result['rec_texts']
    text_result = []
    for idx, item in enumerate(text_list):
        rec_text = item.replace("<UKN>", "")
        text_result.append(rec_text)

    dt_boxes = rescaled_boxes
    rec_res = text_result

    # 두 리스트를 zip으로 묶음
    zipped_boxes_texts = list(zip(dt_boxes, rec_res))

    # 정렬
    error_margin = 8
    sorted_zipped = sorted(zipped_boxes_texts,
                           key=lambda item: (round((item[0][1] + item[0][3] / 2) / error_margin), item[0][0]))

    # 다시 풀어내기
    if sorted_zipped:
        sorted_text_det_bboxes, sorted_text_recognitions = zip(*sorted_zipped)
    else:
        sorted_text_det_bboxes, sorted_text_recognitions = [], []
    # 리스트로 변환
    sorted_text_det_bboxes = list(sorted_text_det_bboxes)
    sorted_text_recognitions = list(sorted_text_recognitions)

    xyxy_dt_boxes = []
    for idx, box_val in enumerate(sorted_text_det_bboxes):
        x, y, w, h = box_val
        xyxy_dt_boxes.append([x, y, x + w, y + h])
    return xyxy_dt_boxes, sorted_text_recognitions


if __name__ == '__main__':
    target_image = '{"image_url": "demo/dummy-table.jpg"}'
    test_image = json.loads(target_image)["image_url"]
    det = 'configs/textdet/dbnetpp/dbnetpp_resnet50-dcnv2_fpnc_1200e_icdar2015.py'
    rec = '/home/najm/mmocr/mmocr_jm/satrn_shallow_5e_st_mj.py'
    det_weights = 'detection_KT_v1.0.0_240726_release.pth'
    rec_weights = 'recognition_KT_v1.0.0_240726_release.pth'
    dt_boxes, rec_res_origin = run_ocr(test_image, det, det_weights, rec, rec_weights)
    print(dt_boxes, rec_res_origin)
