# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""DRIONS-DB (training set) for Optic Disc Segmentation.

The dataset originates from data collected from 55 patients with glaucoma
(23.1%) and eye hypertension (76.9%), and random selected from an eye fundus
image base belonging to the Ophthalmology Service at Miguel Servet Hospital,
Saragossa (Spain).  It contains 110 eye fundus images with a resolution of 600
x 400. Two sets of ground-truth optic disc annotations are available. The first
set is commonly used for training and testing. The second set acts as a "human"
baseline.

* Reference: [DRIONSDB-2008]_
* Original resolution (height x width): 400 x 600
* Configuration resolution: 416 x 608 (after padding)
* Split reference: [MANINIS-2016]_
* Protocols ``expert1`` (baseline) and ``expert2`` (human comparison):

  * Training samples: 60
  * Test samples: 50

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import csv
import importlib.resources
import importlib.resources.abc
import os
import pathlib

import PIL.Image
import PIL.ImageDraw
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
    """A specialized raw-data-loader for the drionsdb dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

    def _txt_to_pil_1(
        self, fname: pathlib.Path, size: tuple[int, int]
    ) -> PIL.Image.Image:
        """Convert DRIONS-DB annotations to image format.

        Parameters
        ----------
        fname
            Path to a file containing annotations.
        size
            The size of the mask (width, height).

        Returns
        -------
            The binary mask.
        """
        with fname.open("r") as f:
            rows = csv.reader(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
            data = list(map(tuple, rows))

        retval = PIL.Image.new("1", size)
        draw = PIL.ImageDraw.ImageDraw(retval)
        draw.polygon(data, fill="white")
        del draw
        return retval

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

        image = PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB")
        target = to_tensor(self._txt_to_pil_1(self.datadir / sample[1], image.size))
        image = to_tensor(image)

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
    """DRIONS-DB (training set) for Optic Disc Segmentation.

    Parameters
    ----------
    split_path
        Path or traversable (resource) with the JSON split description to load.
    """

    def __init__(self, split_path: pathlib.Path | importlib.resources.abc.Traversable):
        super().__init__(
            database_split=JSONDatabaseSplit(split_path),
            raw_data_loader=RawDataLoader(),
            database_name=DATABASE_SLUG,
            split_name=split_path.name.rsplit(".", 2)[0],
            task="segmentation",
        )
