# Copyright (c) OpenMMLab. All rights reserved.
import os.path as osp
from typing import Dict, List, Iterable, Optional, Sequence, Tuple, Union

import cv2
import mmcv
import numpy as np
from mmengine.dataset import Compose
from mmengine.structures import InstanceData

from mmocr.utils import ConfigType
from .base_inferencer import BaseInferencer
from torch import Tensor
from mmengine.dataset import pseudo_collate

from mmengine.registry import FUNCTIONS
import natsort

InstanceList = List[InstanceData]
InputType = Union[str, np.ndarray]
InputsType = Union[InputType, Sequence[InputType]]
PredType = Union[InstanceData, InstanceList]
ImgType = Union[np.ndarray, Sequence[np.ndarray]]
ResType = Union[Dict, List[Dict], InstanceData, List[InstanceData]]

from rich.progress import track


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
        return new_img
    else:
        delta_h = desired_height - origin_h
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = 0, 0
        padding_color = (255, 255, 255)
        new_img = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)

        return new_img


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
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
        # r = height / float(h)
        # dim = (int(w * r), height)

        try:
            r = height / float(h)
            dim = (int(w * r), height)
            print("Result:", r)
        except ZeroDivisionError:
            print("Error: Division by zero is not allowed.")
        except Exception as e:
            print("An unexpected error occurred:", e)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        # r = width / float(w)
        # dim = (width, int(h * r))

        try:
            r = width / float(w)
            dim = (width, int(h * r))
            print("Result:", r)
        except ZeroDivisionError:
            print("Error: Division by zero is not allowed.")
        except Exception as e:
            print("An unexpected error occurred:", e)

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


class BaseMMOCRInferencer(BaseInferencer):
    """Base inferencer.

    Args:
        model (str or ConfigType): Model config or the path to it.
        ckpt (str, optional): Path to the checkpoint.
        device (str, optional): Device to run inference. If None, the best
            device will be automatically used.
        show (bool): Whether to display the image in a popup window.
            Defaults to False.
        wait_time (float): The interval of show (s). Defaults to 0.
        draw_pred (bool): Whether to draw predicted bounding boxes.
            Defaults to True.
        pred_score_thr (float): Minimum score of bboxes to draw.
            Defaults to 0.3.
        img_out_dir (str): Output directory of images. Defaults to ''.
        pred_out_file: File to save the inference results. If left as empty, no
            file will be saved.
        print_result (bool): Whether to print the result.
            Defaults to False.
    """

    func_kwargs = dict(
        preprocess=[],
        forward=[],
        visualize=[
            'show', 'wait_time', 'draw_pred', 'pred_score_thr', 'img_out_dir'
        ],
        postprocess=['print_result', 'pred_out_file', 'get_datasample'])

    def __init__(self,
                 config: Union[ConfigType, str],
                 ckpt: Optional[str],
                 device: Optional[str] = None,
                 **kwargs) -> None:
        # A global counter tracking the number of images processed, for
        # naming of the output images
        self.num_visualized_imgs = 0
        super().__init__(config=config, ckpt=ckpt, device=device, **kwargs)
        self._init_collate(self.cfg)
        self.num_unnamed_imgs = 0

    def _init_pipeline(self, cfg: ConfigType) -> None:
        """Initialize the test pipeline."""
        pipeline_cfg = cfg.test_dataloader.dataset.pipeline

        # For inference, the key of ``instances`` is not used.
        if 'meta_keys' in pipeline_cfg[-1]:
            pipeline_cfg[-1]['meta_keys'] = tuple(
                meta_key for meta_key in pipeline_cfg[-1]['meta_keys']
                if meta_key != 'instances')

        # Loading annotations is also not applicable
        idx = self._get_transform_idx(pipeline_cfg, 'LoadOCRAnnotations')
        if idx != -1:
            del pipeline_cfg[idx]

        self.file_pipeline = Compose(pipeline_cfg)

        load_img_idx = self._get_transform_idx(pipeline_cfg,
                                               'LoadImageFromFile')
        if load_img_idx == -1:
            raise ValueError(
                'LoadImageFromFile is not found in the test pipeline')
        pipeline_cfg[load_img_idx]['type'] = 'LoadImageFromNDArray'
        self.ndarray_pipeline = Compose(pipeline_cfg)

    def pseudo_collate(data_batch: Sequence):
        """Convert list of data sampled from dataset into a batch of data, of which
        type consistent with the type of each data_itement in ``data_batch``.

        The default behavior of dataloader is to merge a list of samples to form
        a mini-batch of Tensor(s). However, in MMEngine, ``pseudo_collate``
        will not stack tensors to batch tensors, and convert int, float, ndarray to
        tensors.

        This code is referenced from:
        `Pytorch default_collate <https://github.com/pytorch/pytorch/blob/master/torch/utils/data/_utils/collate.py>`_.

        Args:
            data_batch (Sequence): Batch of data from dataloader.

        Returns:
            Any: Transversed Data in the same format as the data_itement of
            ``data_batch``.
        """  # noqa: E501
        data_item = data_batch[0]
        data_item_type = type(data_item)
        if isinstance(data_item, (str, bytes)):
            return data_batch
        elif isinstance(data_item, tuple) and hasattr(data_item, '_fields'):
            # named tuple
            return data_item_type(*(pseudo_collate(samples)
                                    for samples in zip(*data_batch)))
        elif isinstance(data_item, Sequence):
            # check to make sure that the data_itements in batch have
            # consistent size
            it = iter(data_batch)
            data_item_size = len(next(it))
            if not all(len(data_item) == data_item_size for data_item in it):
                raise RuntimeError(
                    'each data_itement in list of batch should be of equal size')
            transposed = list(zip(*data_batch))

            if isinstance(data_item, tuple):
                return [pseudo_collate(samples)
                        for samples in transposed]  # Compat with Pytorch.
            else:
                try:
                    return data_item_type(
                        [pseudo_collate(samples) for samples in transposed])
                except TypeError:
                    # The sequence type may not support `__init__(iterable)`
                    # (e.g., `range`).
                    return [pseudo_collate(samples) for samples in transposed]
        elif isinstance(data_item, Mapping):
            return data_item_type({
                key: pseudo_collate([d[key] for d in data_batch])
                for key in data_item
            })
        else:
            return data_batch

    def _init_collate(self, cfg: ConfigType):
        """Initialize the ``collate_fn`` with the given config.

        The returned ``collate_fn`` will be used to collate the batch data.
        If will be used in :meth:`preprocess` like this

        .. code-block:: python
            def preprocess(self, inputs, batch_size, **kwargs):
                ...
                dataloader = map(self.collate_fn, dataloader)
                yield from dataloader

        Args:
            cfg (ConfigType): Config which could contained the `collate_fn`
                information. If `collate_fn` is not defined in config, it will
                be :func:`pseudo_collate`.

        Returns:
            Callable: Collate function.
        """
        try:
            with FUNCTIONS.switch_scope_and_registry(self.scope) as registry:
                self.collate_fn = registry.get(cfg.test_dataloader.collate_fn)
        except AttributeError:
            self.collate_fn = self.pseudo_collate
        # return collate_fn  # type: ignore

    def _get_transform_idx(self, pipeline_cfg: ConfigType, name: str) -> int:
        """Returns the index of the transform in a pipeline.

        If the transform is not found, returns -1.
        """
        for i, transform in enumerate(pipeline_cfg):
            if transform['type'] == name:
                return i
        return -1

    def preprocess(self, inputs: InputsType) -> Dict:
        """Process the inputs into a model-feedable format."""
        results = []
        # print("second")
        for single_input in inputs:
            if isinstance(single_input, str):
                if osp.isdir(single_input):
                    raise ValueError('Feeding a directory is not supported')
                    # for img_path in os.listdir(single_input):
                    #     data_ =dict(img_path=osp.join(single_input,img_path))
                    #     results.append(self.file_pipeline(data_))
                else:
                    data_ = dict(img_path=single_input)
                    results.append(self.file_pipeline(data_))
            elif isinstance(single_input, np.ndarray):
                data_ = dict(img=single_input)
                results.append(self.ndarray_pipeline(data_))
            else:
                raise ValueError(
                    f'Unsupported input type: {type(single_input)}')

        return self._collate(results)

    def preprocess_batch(self, inputs: InputsType):
        """Process the inputs into a model-feedable format.

        Customize your preprocess by overriding this method. Preprocess should
        return an iterable object, of which each item will be used as the
        input of ``model.test_step``.

        ``BaseInferencer.preprocess`` will return an iterable chunked data,
        which will be used in __call__ like this:

        .. code-block:: python

            def __call__(self, inputs, batch_size=1, **kwargs):
                chunked_data = self.preprocess(inputs, batch_size, **kwargs)
                for batch in chunked_data:
                    preds = self.forward(batch, **kwargs)

        Args:
            inputs (InputsType): Inputs given by user.
            batch_size (int): batch size. Defaults to 1.

        Yields:
            Any: Data processed by the ``pipeline`` and ``collate_fn``.
        """
        # print("batch")

        chunked_data = self._get_chunk_data(
            inputs, self.ndarray_pipeline, self.batch_size)

        yield from map(self._collate, chunked_data)

    def collate_batch(self, samples: List[Dict]):
        # preprocessor = TextRecogDataPreprocessor()
        # pre_samples = preprocessor(samples)
        # return pre_samples
        inputs = [sample['inputs'] for sample in samples]
        inputs = torch.cat(inputs, 0)
        # labels = [sample['data_samples'] for sample in samples]
        return {'inputs': inputs, 'data_samples': samples['data_samples']}

    def _get_chunk_data(self, inputs: Iterable, pipeline: None, chunk_size: int):
        """Get batch data from inputs.

        Args:
            inputs (Iterable): An iterable dataset.
            chunk_size (int): Equivalent to batch size.

        Yields:
            list: batch data.
        """
        inputs_iter = iter(inputs)
        while True:
            try:
                chunk_data = []
                for _ in range(chunk_size):
                    inputs_ = next(inputs_iter)
                    if isinstance(inputs_, list):
                        x, y, w, h = inputs_
                        cropped_img = self.input_img[y:y + h, x:x + w, :]
                        img = image_resize(cropped_img, height=32)
                        # step 2. 패딩
                        desired_width = 200
                        new_img = gap_with_pad_width(img, desired_width)
                        # step 3. 100으로 리사이즈 하면 32보다 작은 경우 남는 공간 패딩
                        desired_height = 32
                        new_img = gap_with_pad_height(new_img, desired_height)
                        pipe_out = pipeline(new_img)
                    else:
                        pipe_out = pipeline(inputs_)
                    if pipe_out['data_samples'].get('img_path') is None:
                        pipe_out['data_samples'].set_metainfo(
                            dict(img_path=f'{self.num_unnamed_imgs}.jpg'))
                        self.num_unnamed_imgs += 1
                    # chunk_data.append((inputs_, pipe_out))
                    chunk_data.append(pipe_out)
                yield chunk_data
            except StopIteration:
                if chunk_data:
                    yield chunk_data
                break

    def _collate(self, results: List[Dict]) -> Dict:
        """Collate the results from different images."""
        results = {key: [d[key] for d in results] for key in results[0]}
        return results

    def __call__(self, user_inputs: InputsType, batch_size: int = 1, input_img=None,
                 **kwargs) -> Union[Dict, List[Dict]]:
        """Call the inferencer.

        Args:
            user_inputs: Inputs for the inferencer.
            kwargs: Keyword arguments for the inferencer.
        """
        self.input_img = input_img
        # Detect if user_inputs are in a batch
        is_batch = isinstance(user_inputs, list)
        # inputs = user_inputs if is_batch else [user_inputs]
        inputs = user_inputs

        self.batch_size = batch_size

        params = self._dispatch_kwargs(**kwargs)
        preprocess_kwargs = self.base_params[0].copy()
        preprocess_kwargs.update(params[0])
        forward_kwargs = self.base_params[1].copy()
        forward_kwargs.update(params[1])
        visualize_kwargs = self.base_params[2].copy()
        visualize_kwargs.update(params[2])
        postprocess_kwargs = self.base_params[3].copy()
        postprocess_kwargs.update(params[3])

        # data = self.preprocess(inputs, **preprocess_kwargs)
        # preds = self.forward(data, **forward_kwargs)
        # imgs = self.visualize(inputs, preds, **visualize_kwargs)
        # results = self.postprocess(
        #     preds, imgs, is_batch=is_batch, **postprocess_kwargs)
        ori_inputs = self._inputs_to_list(inputs)
        if is_batch:
            results = []
            inputs = self.preprocess_batch(
                inputs=ori_inputs)
            for i, data in enumerate(track(inputs, description='inference'), start=1):
                preds = self.forward(data, **forward_kwargs)
                imgs = self.visualize(inputs, preds, **visualize_kwargs)
                batch_res = self.postprocess(
                    preds, imgs, is_batch=is_batch, **postprocess_kwargs)
                results.extend(batch_res)
        else:
            data = self.preprocess(
                inputs=ori_inputs, **preprocess_kwargs)
            preds = self.forward(data, **forward_kwargs)
            imgs = self.visualize(inputs, preds, **visualize_kwargs)
            results = self.postprocess(
                preds, imgs, is_batch=is_batch, **postprocess_kwargs)
        # # for ori_inputs, data in track(
        # #         inputs, description='Inference'):
        # preds = self.forward(data, **forward_kwargs)
        # visualization = self.visualize(
        #     ori_inputs, preds, img_out_dir=img_out_dir, **visualize_kwargs)
        # batch_res = self.postprocess(
        #     preds,
        #     visualization,
        #     return_datasamples,
        #     pred_out_dir=pred_out_dir,
        #     **postprocess_kwargs)
        # results['predictions'].extend(batch_res['predictions'])
        # if return_vis and batch_res['visualization'] is not None:
        #     results['visualization'].extend(batch_res['visualization'])
        return results

    def _inputs_to_list(self, inputs: InputsType) -> list:
        """Preprocess the inputs to a list.

        Preprocess inputs to a list according to its type:

        - list or tuple: return inputs
        - str:
            - Directory path: return all files in the directory
            - other cases: return a list containing the string. The string
              could be a path to file, a url or other types of string according
              to the task.

        Args:
            inputs (InputsType): Inputs for the inferencer.

        Returns:
            list: List of input for the :meth:`preprocess`.
        """
        if isinstance(inputs, str):
            import os
            # backend = get_file_backend(inputs)
            if os.path.isdir(inputs):
                # Backends like HttpsBackend do not implement `isdir`, so only
                # those backends that implement `isdir` could accept the inputs
                # as a directory
                filename_list = natsort.natsorted(os.listdir(inputs))
                inputs = [
                    os.path.join(inputs, filename) for filename in filename_list
                ]
        if isinstance(inputs, tuple):
            return inputs
        if not isinstance(inputs, list):
            inputs = [inputs]

        return inputs

    def visualize(self,
                  inputs: InputsType,
                  preds: PredType,
                  show: bool = False,
                  wait_time: int = 0,
                  draw_pred: bool = True,
                  pred_score_thr: float = 0.3,
                  img_out_dir: str = '') -> List[np.ndarray]:
        """Visualize predictions.

        Args:
            inputs (List[Union[str, np.ndarray]]): Inputs for the inferencer.
            preds (List[Dict]): Predictions of the model.
            show (bool): Whether to display the image in a popup window.
                Defaults to False.
            wait_time (float): The interval of show (s). Defaults to 0.
            draw_pred (bool): Whether to draw predicted bounding boxes.
                Defaults to True.
            pred_score_thr (float): Minimum score of bboxes to draw.
                Defaults to 0.3.
            img_out_dir (str): Output directory of images. Defaults to ''.
        """
        if self.visualizer is None or not show and img_out_dir == '':
            return None

        if getattr(self, 'visualizer') is None:
            raise ValueError('Visualization needs the "visualizer" term'
                             'defined in the config, but got None.')

        results = []

        for single_input, pred in zip(inputs, preds):
            if isinstance(single_input, str):
                img = mmcv.imread(single_input)
                img = img[:, :, ::-1]
                img_name = osp.basename(single_input)
            elif isinstance(single_input, np.ndarray):
                img = single_input.copy()
                img_num = str(self.num_visualized_imgs).zfill(8)
                img_name = f'{img_num}.jpg'
            else:
                raise ValueError('Unsupported input type: '
                                 f'{type(single_input)}')

            out_file = osp.join(img_out_dir, img_name) if img_out_dir != '' \
                else None

            self.visualizer.add_datasample(
                img_name,
                img,
                pred,
                show=show,
                wait_time=wait_time,
                draw_gt=False,
                draw_pred=draw_pred,
                pred_score_thr=pred_score_thr,
                out_file=out_file,
            )
            results.append(img)
            self.num_visualized_imgs += 1

        return results

    def postprocess(
            self,
            preds: PredType,
            imgs: Optional[List[np.ndarray]] = None,
            is_batch: bool = False,
            print_result: bool = False,
            pred_out_file: str = '',
            get_datasample: bool = False,
    ) -> Union[ResType, Tuple[ResType, np.ndarray]]:
        """Postprocess predictions.

        Args:
            preds (List[Dict]): Predictions of the model.
            imgs (Optional[np.ndarray]): Visualized predictions.
            is_batch (bool): Whether the inputs are in a batch.
                Defaults to False.
            print_result (bool): Whether to print the result.
                Defaults to False.
            pred_out_file (str): Output file name to store predictions
                without images. Supported file formats are “json2”, “yaml/yml”
                and “pickle/pkl”. Defaults to ''.
            get_datasample (bool): Whether to use Datasample to store
                inference results. If False, dict will be used.

        Returns:
            TODO
        """
        results = preds
        if not get_datasample:
            results = []
            for pred in preds:
                result = self.pred2dict(pred)
                results.append(result)
        if not is_batch:
            results = results[0]
        if print_result:
            print(results)
        # Add img to the results after printing
        if pred_out_file != '':
            mmcv.dump(results, pred_out_file)
        if imgs is None:
            return results
        return results, imgs

    def pred2dict(self, data_sample: InstanceData) -> Dict:
        """Extract elements necessary to represent a prediction into a
        dictionary.

        It's better to contain only basic data elements such as strings and
        numbers in order to guarantee it's json2-serializable.
        """
        raise NotImplementedError

    def _array2list(self, array: Union[Tensor, np.ndarray,
                                       List]) -> List[float]:
        """Convert a tensor or numpy array to a list.

        Args:
            array (Union[Tensor, np.ndarray]): The array to be converted.

        Returns:
            List[float]: The converted list.
        """
        if isinstance(array, Tensor):
            return array.detach().cpu().numpy().tolist()
        if isinstance(array, np.ndarray):
            return array.tolist()
        if isinstance(array, list):
            array = [self._array2list(arr) for arr in array]
        return array