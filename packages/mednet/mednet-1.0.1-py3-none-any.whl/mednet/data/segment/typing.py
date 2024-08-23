# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Define specialized data typing for semantic segmentation tasks."""

import typing

import torch

from ..typing import RawDataLoader as BaseDataLoader


class SegmentationData(typing.TypedDict):
    """Type for segmentation data."""

    image: torch.Tensor
    target: torch.Tensor
    mask: torch.Tensor


Sample: typing.TypeAlias = tuple[SegmentationData, typing.Mapping[str, typing.Any]]


class SegmentationRawDataLoader(BaseDataLoader):
    """Loader object that handles samples and labels from storage."""

    def __init__(self):
        super().__init__()

    def sample(self, sample: tuple[str, str, str | None]) -> Sample:
        """Load whole samples from media.

        Parameters
        ----------
        sample
            Information about the sample to load. Implementation dependent.
        """

        raise NotImplementedError("You must implement the `sample()` method")
