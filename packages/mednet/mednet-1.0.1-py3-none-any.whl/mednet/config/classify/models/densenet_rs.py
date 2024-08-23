# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""DenseNet_, to be trained from scratch.

This configuration contains a version of DenseNet_ (c.f. `TorchVision's
page <densenet_pytorch_>`), modified to have exactly 14 outputs
(matching the number of classes on NIH CXR-14).  It can be used to train
weights from scratch for radiological sign detection.
"""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.densenet
import mednet.models.transforms

model = mednet.models.classify.densenet.Densenet(
    loss_type=torch.nn.BCEWithLogitsLoss,
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=0.0001),
    pretrained=False,
    dropout=0.1,
    num_classes=14,  # number of classes in NIH CXR-14
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
)
