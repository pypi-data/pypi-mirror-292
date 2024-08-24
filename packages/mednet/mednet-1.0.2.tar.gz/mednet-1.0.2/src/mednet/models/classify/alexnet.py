# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""`AlexNet network architecture <alexnet-pytorch_>`_, from [ALEXNET-2012]_."""

import logging
import typing

import torch
import torch.nn
import torch.optim.optimizer
import torch.utils.data
import torchvision.models as models

from ...data.typing import TransformSequence
from .model import Model

logger = logging.getLogger(__name__)


class Alexnet(Model):
    """`AlexNet network architecture <alexnet-pytorch_>`_ model, from [ALEXNET-2012]_.

    Note: only usable with a normalized dataset

    Parameters
    ----------
    loss_type
        The loss to be used for training and evaluation.

        .. warning::

           The loss should be set to always return batch averages (as opposed
           to the batch sum), as our logging system expects it so.
    loss_arguments
        Arguments to the loss.
    optimizer_type
        The type of optimizer to use for training.
    optimizer_arguments
        Arguments to the optimizer after ``params``.
    scheduler_type
        The type of scheduler to use for training.
    scheduler_arguments
        Arguments to the scheduler after ``params``.
    model_transforms
        An optional sequence of torch modules containing transforms to be
        applied on the input **before** it is fed into the network.
    augmentation_transforms
        An optional sequence of torch modules containing transforms to be
        applied on the input **before** it is fed into the network.
    pretrained
        If set to True, loads pretrained model weights during initialization,
        else trains a new model.
    num_classes
        Number of outputs (classes) for this model.
    """

    def __init__(
        self,
        loss_type: type[torch.nn.Module] = torch.nn.BCEWithLogitsLoss,
        loss_arguments: dict[str, typing.Any] = {},
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] = {},
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] = {},
        model_transforms: TransformSequence = [],
        augmentation_transforms: TransformSequence = [],
        pretrained: bool = False,
        num_classes: int = 1,
    ):
        super().__init__(
            name="alexnet",
            loss_type=loss_type,
            loss_arguments=loss_arguments,
            optimizer_type=optimizer_type,
            optimizer_arguments=optimizer_arguments,
            scheduler_type=scheduler_type,
            scheduler_arguments=scheduler_arguments,
            model_transforms=model_transforms,
            augmentation_transforms=augmentation_transforms,
            num_classes=num_classes,
        )

        self.pretrained = pretrained

        # Load pretrained model
        if not pretrained:
            weights = None
        else:
            logger.info(f"Loading pretrained {self.name} model weights")
            weights = models.AlexNet_Weights.DEFAULT

        self.model_ft = models.alexnet(weights=weights)

        # Adapt output features
        self.model_ft.classifier[4] = torch.nn.Linear(4096, 512)
        self.model_ft.classifier[6] = torch.nn.Linear(512, self.num_classes)

    def forward(self, x):
        """Forward the input tensor through the network, producing a prediction.

        Parameters
        ----------
        x
            The tensor input to be forwarded.

        Returns
        -------
            The prediction, as a tensor.
        """
        x = self.normalizer(x)  # type: ignore
        return self.model_ft(x)

    def set_normalizer(self, dataloader: torch.utils.data.DataLoader) -> None:
        """Initialize the normalizer for the current model.

        This function is NOOP if ``pretrained = True`` (normalizer set to
        imagenet weights, during contruction).

        Parameters
        ----------
        dataloader
            A torch Dataloader from which to compute the mean and std.
            Will not be used if the model is pretrained.
        """

        if self.pretrained:
            from .normalizer import make_imagenet_normalizer

            logger.warning(
                f"ImageNet pre-trained {self.name} model - NOT "
                f"computing z-norm factors from train dataloader. "
                f"Using preset factors from torchvision.",
            )
            self.normalizer = make_imagenet_normalizer()
        else:
            super().set_normalizer(dataloader)
