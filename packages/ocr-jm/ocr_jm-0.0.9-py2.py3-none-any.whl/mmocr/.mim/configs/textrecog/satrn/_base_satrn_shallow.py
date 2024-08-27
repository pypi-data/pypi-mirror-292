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
