# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Drishti-GS1 for Optic Disc and Cup Segmentation.

Drishti-GS is a dataset meant for validation of segmenting OD, cup and
detecting notching.  The images in the Drishti-GS dataset have been collected
and annotated by Aravind Eye hospital, Madurai, India. This dataset is of a
single population as all subjects whose eye images are part of this dataset are
Indians.

The dataset is divided into two: a training set and a testing set of images.
Training images (50) are provided with groundtruths for OD and Cup segmentation
and notching information.

* Reference (including train/test split): [DRISHTIGS1-2014]_
* Original resolution (height x width): varying (min: 1749x2045 pixels,
  max: 1845x2468 pixels)
* Protocols ``optic-disc`` and ``optic-cup``:

  * Training: 50
  * Test: 51

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources
import importlib.resources.abc
import os
import pathlib

import PIL.Image
from torchvision import tv_tensors
from torchvision.transforms.functional import to_tensor

from ...models.transforms import crop_image_to_mask
from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..split import JSONDatabaseSplit
from .typing import Sample, SegmentationRawDataLoader

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name to refer to this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(SegmentationRawDataLoader):
    """A specialized raw-data-loader for the drishtigs1 dataset.

    Parameters
    ----------
    target_all
        Indicate whether to use the "all" or "any" target.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self, target_all: bool):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

        self.target_all = target_all

    def sample(self, sample: tuple[str, str, str | None]) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing path suffixes to the sample image, target, and mask
            to be loaded, within the dataset root folder.

        Returns
        -------
            The sample representation.
        """

        image = to_tensor(PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB"))

        if self.target_all:
            target = to_tensor(
                PIL.Image.open(self.datadir / sample[1])
                .convert(mode="RGB", dither=None)
                .convert("L")
                .point(lambda p: p > 254, mode="1")
            )
        else:
            target = to_tensor(
                PIL.Image.open(self.datadir / sample[1])
                .convert(mode="RGB", dither=None)
                .convert("L")
                .point(lambda p: p > 0, mode="1")
            )

        assert sample[2] is not None
        mask_path = (
            importlib.resources.files(__package__) / "masks" / DATABASE_SLUG / sample[2]
        )
        with importlib.resources.as_file(mask_path) as path:
            mask = to_tensor(PIL.Image.open(path).convert(mode="1", dither=None))

        image = tv_tensors.Image(crop_image_to_mask(image, mask))
        target = tv_tensors.Mask(crop_image_to_mask(target, mask))
        mask = tv_tensors.Mask(crop_image_to_mask(mask, mask))

        return dict(image=image, target=target, mask=mask), dict(name=sample[0])  # type: ignore[arg-type]


class DataModule(CachingDataModule):
    """Drishti-GS1 for Optic Disc and Cup Segmentation.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    target_all
        Indicate whether to use the "all" or "any" target.
    """

    def __init__(
        self,
        split_path: pathlib.Path | importlib.resources.abc.Traversable,
        target_all: bool,
    ):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(target_all),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="segmentation",
        )
