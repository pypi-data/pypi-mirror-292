# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`AlexNet network architecture <alexnet-pytorch_>`_, to be trained from scratch."""

import torch.nn
import torch.optim
import torchvision.transforms
import torchvision.transforms.v2

import mednet.models.classify.alexnet
import mednet.models.transforms

model = mednet.models.classify.alexnet.Alexnet(
    loss_type=torch.nn.BCEWithLogitsLoss,
    optimizer_type=torch.optim.Adam,
    optimizer_arguments=dict(lr=0.001),
    pretrained=False,
    model_transforms=[
        mednet.models.transforms.SquareCenterPad(),
        torchvision.transforms.v2.Resize(512, antialias=True),
        torchvision.transforms.v2.RGB(),
    ],
)
