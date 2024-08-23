# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import copy
import logging
import typing

import lightning.pytorch as pl
import torch
import torch.nn
import torch.optim.lr_scheduler
import torch.optim.optimizer
import torch.utils.data
import torchvision.transforms

from ..data.typing import TransformSequence
from .loss_weights import get_positive_weights
from .typing import Checkpoint

logger = logging.getLogger(__name__)


class Model(pl.LightningModule):
    """Base class for models.

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
        super().__init__()

        self.name = name
        self.num_classes = num_classes
        self.model_transforms = model_transforms
        self._loss_type = loss_type
        self._train_loss_arguments = copy.deepcopy(loss_arguments)
        self._validation_loss_arguments = copy.deepcopy(loss_arguments)
        self._optimizer_type = optimizer_type
        self._optimizer_arguments = optimizer_arguments
        self._scheduler_type = scheduler_type
        self._scheduler_arguments = scheduler_arguments
        self.augmentation_transforms = augmentation_transforms

        # initializes losses from input arguments
        self._configure_losses()

    @property
    def augmentation_transforms(self) -> torchvision.transforms.Compose:
        return self._augmentation_transforms

    @augmentation_transforms.setter
    def augmentation_transforms(self, v: TransformSequence):
        self._augmentation_transforms = torchvision.transforms.Compose(v)

        if len(v) != 0:
            transforms_str = ", ".join(
                [
                    f"{type(k).__module__}.{str(k)}"
                    for k in self._augmentation_transforms.transforms
                ]
            )
            logger.info(f"Data augmentations: {transforms_str}")
        else:
            logger.info("Data augmentations: None")

    def forward(self, x):
        raise NotImplementedError

    def on_save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Perform actions during checkpoint saving (called by lightning).

        Called by Lightning when saving a checkpoint to give you a chance to
        store anything else you might want to save. Use on_load_checkpoint() to
        restore what additional data is saved here.

        Parameters
        ----------
        checkpoint
            The checkpoint to save.
        """

        checkpoint["normalizer"] = self.normalizer

    def on_load_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Perform actions during model loading (called by lightning).

        If you saved something with on_save_checkpoint() this is your chance to
        restore this.

        Parameters
        ----------
        checkpoint
            The loaded checkpoint.
        """

        logger.info("Restoring normalizer from checkpoint.")
        self.normalizer = checkpoint["normalizer"]

    def set_normalizer(self, dataloader: torch.utils.data.DataLoader) -> None:
        raise NotImplementedError

    def training_step(self, batch, _):
        raise NotImplementedError

    def validation_step(self, batch, batch_idx, dataloader_idx=0):
        raise NotImplementedError

    def predict_step(self, batch, batch_idx, dataloader_idx=0):
        raise NotImplementedError

    def _configure_losses(self):
        """Create loss objects for train and validation."""

        logger.info(f"Configuring train loss ({self._train_loss_arguments})...")
        self._train_loss = self._loss_type(**self._train_loss_arguments)
        logger.info(
            f"Configuring validation loss ({self._validation_loss_arguments})..."
        )
        self._validation_loss = self._loss_type(**self._validation_loss_arguments)

    def configure_optimizers(self):
        optimizer = self._optimizer_type(
            self.parameters(),
            **self._optimizer_arguments,
        )

        if self._scheduler_type is None:
            return optimizer

        scheduler = self._scheduler_type(
            optimizer,
            **self._scheduler_arguments,
        )
        return [optimizer], [scheduler]

    def to(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Self:
        """Move model, augmentations and losses to specified device.

        Refer to the method :py:meth:`torch.nn.Module.to` for details.

        Parameters
        ----------
        *args
            Parameter forwarded to the underlying implementations.
        **kwargs
            Parameter forwarded to the underlying implementations.

        Returns
        -------
            Self.
        """

        super().to(*args, **kwargs)

        self._augmentation_transforms = torchvision.transforms.Compose(
            [
                k.to(*args, **kwargs)
                for k in self._augmentation_transforms.transforms
                if hasattr(k, "to")
            ]
        )

        self._train_loss.to(*args, **kwargs)
        self._validation_loss.to(*args, **kwargs)

        return self

    def balance_losses(self, datamodule) -> None:
        """Balance the loss based on the distribution of targets in the datamodule, if the loss supports it (contains a 'pos_weight' attribute).

        Parameters
        ----------
        datamodule
            Instance of a datamodule.
        """

        try:
            getattr(self._loss_type(), "pos_weight")

        except AttributeError:
            logger.warning(
                f"Loss {self._loss_type} does not posess a 'pos_weight' attribute and will not be balanced."
            )

        else:
            train_weights = get_positive_weights(datamodule.train_dataloader())
            self._train_loss_arguments["pos_weight"] = train_weights
            logger.info(
                f"Balanced training loss {self._loss_type}: "
                f"`pos_weight={train_weights}`."
            )

            if "validation" in datamodule.val_dataloader().keys():
                validation_weights = get_positive_weights(
                    datamodule.val_dataloader()["validation"]
                )
            else:
                logger.warning(
                    "Datamodule does not contain a validation dataloader. "
                    "The training dataloader will be used instead."
                )
                validation_weights = get_positive_weights(datamodule.train_dataloader())

            self._validation_loss_arguments["pos_weight"] = validation_weights
            logger.info(
                f"Balanced validation loss {self._loss_type}: "
                f"`pos_weight={validation_weights}`."
            )

        # re-instantiates losses for train and validation
        self._configure_losses()
