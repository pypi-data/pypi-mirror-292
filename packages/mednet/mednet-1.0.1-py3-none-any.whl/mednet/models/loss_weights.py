# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import typing
from collections import Counter

import torch
import torch.utils.data

logger = logging.getLogger(__name__)


def compute_binary_weights(targets):
    """Compute the positive weights when using binary targets.

    Parameters
    ----------
        targets
            A tensor of integer values of length n.

    Returns
    -------
        The positive weights per class.
    """
    class_sample_count = [
        float((targets == t).sum().item()) for t in torch.unique(targets, sorted=True)
    ]

    # Divide negatives by positives
    return torch.tensor(
        [class_sample_count[0] / class_sample_count[1]],
    ).reshape(-1)


def compute_multiclass_weights(targets):
    """Compute the positive weights when using exclusive, multiclass targets.

    Parameters
    ----------
        targets
            A [C x n] tensor of integer values, where `C` is the number of target classes and `n` the number of samples.

    Returns
    -------
        The positive weights per class.
    """

    class_sample_count = torch.sum(targets, dim=1)
    negative_class_sample_count = (
        torch.full((targets.size()[0],), float(targets.size()[1])) - class_sample_count
    )

    return negative_class_sample_count / (
        class_sample_count + negative_class_sample_count
    )


def compute_non_exclusive_multiclass_weights(targets):
    """Compute the positive weights when using non-exclusive, multiclass targets.

    Parameters
    ----------
        targets
            A [C x n] tensor of integer values, where `C` is the number of target classes and `n` the number of samples.

    Returns
    -------
        The positive weights per class.
    """
    raise ValueError(
        "Computing weights of multi-class, non-exclusive labels is not yet supported."
    )


def is_multicalss_exclusive(targets: torch.Tensor) -> bool:
    """Given a [C x n] tensor of integer targets, checks whether samples can only belong to a single class.

    Parameters
    ----------
    targets
        A [C x n] tensor of integer values, where `C` is the number of target classes and `n` the number of samples.

    Returns
    -------
        True if all samples belong to a single class, False otherwise (a sample can belong to multiple classes).
    """
    max_counts = []
    transposed_targets = torch.transpose(targets, 0, 1)
    for t in transposed_targets:
        filtered_list = [i for i in t.tolist() if i != 2]
        counts = Counter(filtered_list)
        max_counts.append(max(counts.values()))

    if set(max_counts) == {1}:
        return True

    return False


def tensor_to_list(tensor) -> list[typing.Any]:
    """Convert a torch.Tensor to a list.

    This is necessary, as torch.tolist returns an int when then tensor contains a single value.

    Parameters
    ----------
    tensor
        The tensor to convert to a list.

    Returns
    -------
        The tensor converted to a list.
    """

    tensor = tensor.tolist()
    if isinstance(tensor, int):
        return [tensor]
    return tensor


def get_positive_weights(
    dataloader: torch.utils.data.DataLoader,
) -> torch.Tensor:
    """Compute the weights of each class of a DataLoader.

    This function inputs a pytorch DataLoader and computes the ratio between
    number of negative and positive samples (scalar).  The weight can be used
    to adjust minimisation criteria to in cases there is a huge data imbalance.

    It returns a vector with weights (inverse counts) for each target.

    Parameters
    ----------
    dataloader
        A DataLoader from which to compute the positive weights.  Entries must
        be a dictionary which must contain a ``target`` key.

    Returns
    -------
        The positive weight of each class in the dataset given as input.
    """

    from collections import defaultdict

    targets = defaultdict(list)

    for batch in dataloader:
        for class_idx, class_targets in enumerate(batch[1]["target"]):
            # Targets are either a single tensor (binary case) or a list of tensors (multilabel)
            if isinstance(batch[1]["target"], list):
                targets[class_idx].extend(tensor_to_list(class_targets))
            else:
                targets[0].extend(tensor_to_list(class_targets))

    targets_list = []
    for k in sorted(list(targets.keys())):
        targets_list.append(targets[k])

    targets_tensor = torch.tensor(targets_list)

    if targets_tensor.shape[0] == 1:
        logger.info("Computing positive weights assuming binary targets.")
        positive_weights = compute_binary_weights(targets_tensor)
    else:
        if is_multicalss_exclusive(targets_tensor):
            logger.info(
                "Computing positive weights assuming multiclass, exclusive targets."
            )
            positive_weights = compute_multiclass_weights(targets_tensor)
        else:
            logger.info(
                "Computing positive weights assuming multiclass, non-exclusive targets."
            )
            positive_weights = compute_non_exclusive_multiclass_weights(targets_tensor)

    return positive_weights
