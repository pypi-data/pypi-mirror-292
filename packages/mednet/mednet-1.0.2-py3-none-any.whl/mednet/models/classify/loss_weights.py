# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Helpers for computing (sample/label) weights for loss terms."""

import logging

import torch
import torch.utils.data

from ...data.typing import DataLoader

logger = logging.getLogger(__name__)


def _get_label_weights(
    dataloader: torch.utils.data.DataLoader,
) -> torch.Tensor:
    """Compute the weights of each class of a DataLoader.

    This function inputs a pytorch DataLoader and computes the ratio between
    number of negative and positive samples (scalar).  The weight can be used
    to adjust minimisation criteria to in cases there is a huge data imbalance.

    It returns a vector with weights (inverse counts) for each label.

    Parameters
    ----------
    dataloader
        A DataLoader from which to compute the positive weights.  Entries must
        be a dictionary which must contain a ``label`` key.

    Returns
    -------
    torch.Tensor
        The positive weight of each class in the dataset given as input.
    """

    targets = torch.tensor(
        [sample for batch in dataloader for sample in batch[1]["target"]],
    )

    # Binary labels
    if len(list(targets.shape)) == 1:
        class_sample_count = [
            float((targets == t).sum().item())
            for t in torch.unique(targets, sorted=True)
        ]

        # Divide negatives by positives
        positive_weights = torch.tensor(
            [class_sample_count[0] / class_sample_count[1]],
        ).reshape(-1)

    # Multiclass labels
    else:
        class_sample_count = torch.sum(targets, dim=0)
        negative_class_sample_count = (
            torch.full((targets.size()[1],), float(targets.size()[0]))
            - class_sample_count
        )

        positive_weights = negative_class_sample_count / (
            class_sample_count + negative_class_sample_count
        )

    return positive_weights


def make_balanced_bcewithlogitsloss(
    dataloader: DataLoader,
) -> torch.nn.BCEWithLogitsLoss:
    """Return a balanced binary-cross-entropy loss.

    The loss is weighted using the ratio between positives and total examples
    available.

    Parameters
    ----------
    dataloader
        The DataLoader to use to compute the BCE weights.

    Returns
    -------
    torch.nn.BCEWithLogitsLoss
        An instance of the weighted loss.
    """

    weights = _get_label_weights(dataloader)
    return torch.nn.BCEWithLogitsLoss(pos_weight=weights)
