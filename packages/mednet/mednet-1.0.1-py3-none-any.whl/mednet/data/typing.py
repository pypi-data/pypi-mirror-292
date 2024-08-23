# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defines most common types used in code."""

import collections.abc
import typing

import torch
import torch.utils.data

Sample: typing.TypeAlias = tuple[
    typing.Mapping[str, typing.Any], typing.Mapping[str, typing.Any]
]
"""Definition of a sample.

First parameter
    The actual data that is input to the model

Second parameter
    A dictionary containing a named set of meta-data.  One the most common is
    the ``target`` entry.
"""


class RawDataLoader:
    """A loader object can load samples from storage."""

    def sample(self, sample: typing.Any) -> Sample:
        """Load whole samples from media.

        Parameters
        ----------
        sample
            Information about the sample to load. Implementation dependent.
        """

        raise NotImplementedError("You must implement the `sample()` method")


Transform: typing.TypeAlias = typing.Callable[[torch.Tensor], torch.Tensor]
"""A callable that transforms tensors into (other) tensors.

Typically used in data-processing pipelines inside pytorch.
"""

TransformSequence: typing.TypeAlias = typing.Sequence[Transform]
"""A sequence of transforms."""

DatabaseSplit: typing.TypeAlias = collections.abc.Mapping[
    str,
    typing.Sequence[typing.Any],
]
"""The definition of a database split.

A database split maps dataset (subset) names to sequences of objects that,
through a :py:class:`RawDataLoader`, eventually becomes a :py:data:`.Sample` in
the processing pipeline.
"""

ConcatDatabaseSplit: typing.TypeAlias = collections.abc.Mapping[
    str,
    typing.Sequence[tuple[typing.Sequence[typing.Any], RawDataLoader]],
]
"""The definition of a complex database split composed of several other splits.

A database split maps dataset (subset) names to sequences of objects that,
through a :py:class:`.RawDataLoader`, eventually becomes a :py:data:`.Sample` in
the processing pipeline. Objects of this subtype allow the construction of
complex splits composed of cannibalized parts of other splits.  Each split may
be assigned a different :py:class:`.RawDataLoader`.
"""


class Dataset(torch.utils.data.Dataset[Sample], typing.Iterable, typing.Sized):
    """Our own definition of a pytorch Dataset.

    We iterate over Sample objects in this case.  Our datasets always
    provide a dunder len method.
    """

    def targets(self) -> list[int | list[int]]:
        """Return the integer targets for all samples in the dataset."""
        raise NotImplementedError("You must implement the `targets()` method")


DataLoader: typing.TypeAlias = torch.utils.data.DataLoader[Sample]
"""Our own augmentation definition of a pytorch DataLoader.

We iterate over Sample objects in this case.
"""
