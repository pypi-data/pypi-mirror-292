# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Definition of base model type for classification tasks."""

import logging
import typing

import torch
import torch.nn
import torch.optim.optimizer
import torch.utils.data

from ...data.typing import TransformSequence
from ..model import Model as BaseModel

logger = logging.getLogger(__name__)


class Model(BaseModel):
    """Base model type for classification tasks.

    Parameters
    ----------
    name
        Common name to give to models of this type.
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
    num_classes
        Number of outputs (classes) for this model.
    """

    def __init__(
        self,
        name: str,
        loss_type: type[torch.nn.Module] = torch.nn.BCEWithLogitsLoss,
        loss_arguments: dict[str, typing.Any] = {},
        optimizer_type: type[torch.optim.Optimizer] = torch.optim.Adam,
        optimizer_arguments: dict[str, typing.Any] = {},
        scheduler_type: type[torch.optim.lr_scheduler.LRScheduler] | None = None,
        scheduler_arguments: dict[str, typing.Any] = {},
        model_transforms: TransformSequence = [],
        augmentation_transforms: TransformSequence = [],
        num_classes: int = 1,
    ):
        super().__init__(
            name,
            loss_type,
            loss_arguments,
            optimizer_type,
            optimizer_arguments,
            scheduler_type,
            scheduler_arguments,
            model_transforms,
            augmentation_transforms,
            num_classes,
        )

    def set_normalizer(self, dataloader: torch.utils.data.DataLoader) -> None:
        """Initialize the input normalizer for the current model.

        Parameters
        ----------
        dataloader
            A torch Dataloader from which to compute the mean and std.
        """

        from .normalizer import make_z_normalizer

        logger.info(
            f"Uninitialised {self.name} model - "
            f"computing z-norm factors from train dataloader.",
        )
        self.normalizer = make_z_normalizer(dataloader)

    def training_step(self, batch, _):
        images = batch[0]["image"]
        labels = batch[1]["target"]

        # Increase label dimension if too low
        # Allows single and multiclass usage
        if labels.ndim == 1:
            labels = torch.reshape(labels, (labels.shape[0], 1))

        # Forward pass on the network
        outputs = self(self.augmentation_transforms(images))

        return self._train_loss(outputs, labels.float())

    def validation_step(self, batch, batch_idx, dataloader_idx=0):
        images = batch[0]["image"]
        labels = batch[1]["target"]

        # Increase label dimension if too low
        # Allows single and multiclass usage
        if labels.ndim == 1:
            labels = torch.reshape(labels, (labels.shape[0], 1))

        # debug code to inspect images by eye:
        # from torchvision.transforms.functional import to_pil_image
        # for k in images:
        #    to_pil_image(k).show()
        #    __import__("pdb").set_trace()

        # data forwarding on the existing network
        outputs = self(images)
        return self._validation_loss(outputs, labels.float())

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        outputs = self(batch[0]["image"])
        return torch.sigmoid(outputs)
