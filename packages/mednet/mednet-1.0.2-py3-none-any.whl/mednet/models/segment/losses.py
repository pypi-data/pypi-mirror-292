# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Specialized losses for semanatic segmentation."""

import torch


class WeightedBCELogitsLoss(torch.nn.Module):
    """Calculates sum of weighted cross entropy loss.

    Implements Equation 1 in [MANINIS-2016]_.  The weight depends on the
    current proportion between negatives and positives in the ground-
    truth sample being analyzed.
    """

    def __init__(self):
        super().__init__()

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Value produced by the model to be evaluated, with the shape ``[n, c,
            h, w]``.
        target
            Ground-truth information with the shape ``[n, c, h, w]``.

        Returns
        -------
            The average loss for all input data.
        """

        # calculates the proportion of negatives to the total number of pixels
        # available in the masked region
        num_pos = target.sum()
        return torch.nn.functional.binary_cross_entropy_with_logits(
            input_,
            target,
            reduction="mean",
            pos_weight=(input_.shape.numel() - num_pos) / num_pos,
        )


class SoftJaccardBCELogitsLoss(torch.nn.Module):
    r"""Implement the generalized loss function of Equation (3) in.

    [IGLOVIKOV-2018]_, with J being the Jaccard distance, and H, the Binary
    Cross-Entropy Loss:

    .. math::

       L = \alpha H + (1-\alpha)(1-J)

    Our implementation is based on :py:class:`torch.nn.BCEWithLogitsLoss`.

    Parameters
    ----------
    alpha
        Determines the weighting of J and H. Default: ``0.7``.
    """

    def __init__(self, alpha: float = 0.7):
        super().__init__()
        self.alpha = alpha

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Value produced by the model to be evaluated, with the shape ``[n, c,
            h, w]``.
        target
            Ground-truth information with the shape ``[n, c, h, w]``.

        Returns
        -------
            Loss, in a single entry.
        """

        eps = 1e-8
        probabilities = torch.sigmoid(input_)
        intersection = (probabilities * target).sum()
        sums = probabilities.sum() + target.sum()
        j = intersection / (sums - intersection + eps)

        # this implements the support for looking just into the RoI
        h = torch.nn.functional.binary_cross_entropy_with_logits(
            input_, target, reduction="mean"
        )
        return (self.alpha * h) + ((1 - self.alpha) * (1 - j))


class MultiWeightedBCELogitsLoss(WeightedBCELogitsLoss):
    """Weighted Binary Cross-Entropy Loss for multi-layered inputs (e.g. for
    Holistically-Nested Edge Detection in [XIE-2015]_).
    """

    def __init__(self):
        super().__init__()

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Value produced by the model to be evaluated, with the shape ``[L,
            n, c, h, w]``.
        target
            Ground-truth information with the shape ``[n, c, h, w]``.

        Returns
        -------
            The average loss for all input data.
        """

        return torch.cat(
            [
                super(MultiWeightedBCELogitsLoss, self).forward(i, target).unsqueeze(0)
                for i in input_
            ]
        ).mean()


class MultiSoftJaccardBCELogitsLoss(SoftJaccardBCELogitsLoss):
    """Implement Equation 3 in [IGLOVIKOV-2018]_ for the multi-output networks
    such as HED or Little W-Net.

    Parameters
    ----------
    alpha : float
        Determines the weighting of SoftJaccard and BCE. Default: ``0.3``.
    """

    def __init__(self, alpha: float = 0.7):
        super().__init__(alpha=alpha)

    def forward(self, input_: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Parameters
        ----------
        input_
            Value produced by the model to be evaluated, with the shape ``[L,
            n, c, h, w]``.
        target
            Ground-truth information with the shape ``[n, c, h, w]``.

        Returns
        -------
            The average loss for all input data.
        """

        return torch.cat(
            [
                super(MultiSoftJaccardBCELogitsLoss, self)
                .forward(i, target)
                .unsqueeze(0)
                for i in input_
            ]
        ).mean()
