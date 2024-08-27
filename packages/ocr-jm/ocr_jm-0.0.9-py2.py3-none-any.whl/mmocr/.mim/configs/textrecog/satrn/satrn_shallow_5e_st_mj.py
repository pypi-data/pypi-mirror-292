default_scope = 'mmocr'
env_cfg = dict(
    cudnn_benchmark=False,
    mp_cfg=dict(mp_start_method='fork', opencv_num_threads=0),
    dist_cfg=dict(backend='nccl'),
)
randomness = dict(seed=None)

default_hooks = dict(
    timer=dict(type='IterTimerHook'),
    logger=dict(type='LoggerHook', interval=5),
    param_scheduler=dict(type='ParamSchedulerHook'),
    checkpoint=dict(type='CheckpointHook', interval=20),
    sampler_seed=dict(type='DistSamplerSeedHook'),
    sync_buffer=dict(type='SyncBuffersHook'),
    visualization=dict(
        type='VisualizationHook',
        interval=1,
        enable=False,
        show=False,
        draw_gt=False,
        draw_pred=False),
)

# Logging
log_level = 'INFO'
log_processor = dict(type='LogProcessor', window_size=10, by_epoch=True)

load_from = None
resume = False

# Evaluation
val_evaluator = dict(type='HmeanIOUMetric')
test_evaluator = val_evaluator

# Visualization
vis_backends = [dict(type='LocalVisBackend')]
visualizer = dict(
    type='TextDetLocalVisualizer',
    name='visualizer',
    vis_backends=vis_backends)

file_client_args = dict(backend='disk')

dictionary = dict(
    type='Dictionary',
    dict_file='{{ fileDirname }}/../../../dicts/MergedChar.txt',
    with_padding=True,
    with_unknown=True,
    same_start_end=True,
    with_start=True,
    with_end=True)

model = dict(
    type='SATRN',
    backbone=dict(type='ShallowCNN', input_channels=3, hidden_dim=512),
    encoder=dict(
        type='SATRNEncoder',
        n_layers=12,
        n_head=8,
        d_k=512 // 8,
        d_v=512 // 8,
        d_model=512,
        n_position=200,
        d_inner=512 * 4,
        dropout=0.1),
    decoder=dict(
        type='NRTRDecoder',
        n_layers=6,
        d_embedding=512,
        n_head=8,
        d_model=512,
        d_inner=512 * 4,
        d_k=512 // 8,
        d_v=512 // 8,
        module_loss=dict(
            type='CEModuleLoss', flatten=True, ignore_first_char=True),
        dictionary=dictionary,
        max_seq_len=24,
        postprocessor=dict(type='AttentionPostprocessor'),
        caching=True),
        data_preprocessor=dict(
        type='TextRecogDataPreprocessor'
    ))
        # mean=[123.675, 116.28, 103.53],
        # std=[58.395, 57.12, 57.375]))

train_pipeline = [
    dict(
        type='LoadImageFromFile',
        file_client_args=file_client_args,
        ignore_empty=True,
        min_size=2),
    dict(type='LoadOCRAnnotations', with_text=True),
    dict(
      type='TorchVisionWrapper',
      op='ColorJitter',
      brightness=32.0 / 255,
      saturation=0.5
    ),
    dict(type='Resize', scale=(200, 32), keep_ratio=False),
    dict(
        type='PackTextRecogInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'valid_ratio'))
]

# TODO Add Test Time Augmentation `MultiRotateAugOCR`
test_pipeline = [
    dict(type='LoadImageFromFile', file_client_args=file_client_args),
    dict(type='Resize', scale=(200, 32), keep_ratio=False),
    dict(
      type='TorchVisionWrapper',
      op='ColorJitter',
      brightness=32.0 / 255,
      saturation=0.5
    ),
    # add loading annotation after ``Resize`` because ground truth
    # does not need to do resize data transform
    dict(type='LoadOCRAnnotations', with_text=True),
    dict(
        type='PackTextRecogInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'valid_ratio'))
]

# from ../_base_._
train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=20, val_interval=1)

# dataset settings
mjsynth_textrecog_data_root = 'data/mjsynth'

mjsynth_textrecog_train = dict(
    type='OCRDataset',
    data_root=mjsynth_textrecog_data_root,
    ann_file='textrecog_train.json',
    pipeline=None)

mjsynth_sub_textrecog_train = dict(
    type='OCRDataset',
    data_root=mjsynth_textrecog_data_root,
    ann_file='subset_textrecog_train.json',
    pipeline=None)

cute80_textrecog_data_root = 'data/cute80'

cute80_textrecog_test = dict(
    type='OCRDataset',
    data_root=cute80_textrecog_data_root,
    ann_file='textrecog_test.json',
    test_mode=True,
    pipeline=None)

iiit5k_textrecog_data_root = 'data/iiit5k'

iiit5k_textrecog_train = dict(
    type='OCRDataset',
    data_root=iiit5k_textrecog_data_root,
    ann_file='textrecog_train.json',
    pipeline=None)

iiit5k_textrecog_test = dict(
    type='OCRDataset',
    data_root=iiit5k_textrecog_data_root,
    ann_file='textrecog_test.json',
    test_mode=True,
    pipeline=None)

svt_textrecog_data_root = 'data/svt'

svt_textrecog_train = dict(
    type='OCRDataset',
    data_root=svt_textrecog_data_root,
    ann_file='textrecog_train.json',
    pipeline=None)

svt_textrecog_test = dict(
    type='OCRDataset',
    data_root=svt_textrecog_data_root,
    ann_file='textrecog_test.json',
    test_mode=True,
    pipeline=None)
svtp_textrecog_data_root = 'data/svtp'

svtp_textrecog_train = dict(
    type='OCRDataset',
    data_root=svtp_textrecog_data_root,
    ann_file='textrecog_train.json',
    pipeline=None)

svtp_textrecog_test = dict(
    type='OCRDataset',
    data_root=svtp_textrecog_data_root,
    ann_file='textrecog_test.json',
    test_mode=True,
    pipeline=None)
icdar2013_textrecog_data_root = 'data/icdar2013'

icdar2013_textrecog_train = dict(
    type='OCRDataset',
    data_root=icdar2013_textrecog_data_root,
    ann_file='textrecog_train.json',
    pipeline=None)

icdar2013_textrecog_test = dict(
    type='OCRDataset',
    data_root=icdar2013_textrecog_data_root,
    ann_file='textrecog_test.json',
    test_mode=True,
    pipeline=None)

icdar2013_857_textrecog_test = dict(
    type='OCRDataset',
    data_root=icdar2013_textrecog_data_root,
    ann_file='textrecog_test_857.json',
    test_mode=True,
    pipeline=None)
icdar2015_textrecog_data_root = 'data/icdar2015'

icdar2015_textrecog_train = dict(
    type='OCRDataset',
    data_root=icdar2015_textrecog_data_root,
    ann_file='textrecog_train.json',
    pipeline=None)

icdar2015_textrecog_test = dict(
    type='OCRDataset',
    data_root=icdar2015_textrecog_data_root,
    ann_file='textrecog_test.json',
    test_mode=True,
    pipeline=None)

icdar2015_1811_textrecog_test = dict(
    type='OCRDataset',
    data_root=icdar2015_textrecog_data_root,
    ann_file='textrecog_test_1811.json',
    test_mode=True,
    pipeline=None)

train_list = [mjsynth_textrecog_train]
test_list = [
    cute80_textrecog_test, iiit5k_textrecog_test,
    svt_textrecog_test, svtp_textrecog_test,
    icdar2013_textrecog_test, icdar2015_textrecog_test
]

train_dataset = dict(
    type='ConcatDataset', datasets=train_list, pipeline=train_pipeline)
test_dataset = dict(
    type='ConcatDataset', datasets=test_list, pipeline=test_pipeline)

# optimizer
optim_wrapper = dict(type='OptimWrapper', optimizer=dict(type='Adam', lr=3e-4))

train_dataloader = dict(
    batch_size=128,
    num_workers=24,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=train_dataset)

test_dataloader = dict(
    batch_size=1,
    num_workers=4,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=test_dataset)

val_dataloader = test_dataloader

val_evaluator = dict(
    dataset_prefixes=['CUTE80', 'IIIT5K', 'SVT', 'SVTP', 'IC13', 'IC15'])
test_evaluator = val_evaluator

auto_scale_lr = dict(base_batch_size=64 * 8)
