# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Define specialized data typing for classification tasks."""

import typing

import torch

from ..typing import RawDataLoader as BaseDataLoader

Sample: typing.TypeAlias = tuple[torch.Tensor, typing.Mapping[str, typing.Any]]


class ClassificationRawDataLoader(BaseDataLoader):
    """A loader object can load samples and labels from storage for classification tasks."""

    def __init__(self):
        super().__init__()

    def sample(self, sample: tuple[str, int, typing.Any | None]) -> Sample:
        """Load whole samples from media.

        Parameters
        ----------
        sample
            Information about the sample to load. Implementation dependent.
        """

        raise NotImplementedError("You must implement the `sample()` method")

    def target(self, k: typing.Any) -> int | list[int]:
        """Load only sample target from media.

        If you do not override this implementation, then, by default,
        this method will call :py:meth:`sample` to load the whole sample
        and extract the label.

        Parameters
        ----------
        k
            The sample to load. This is implementation-dependent.

        Returns
        -------
        int | list[int]
            The label corresponding to the specified sample.
        """

        return self.sample(k)[1]["target"]
