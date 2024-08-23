# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""STARE dataset for vessel segmentation.

A subset of the original STARE dataset contains 20 annotated eye fundus images
with a resolution of 700 x 605 (width x height). Two sets of ground-truth
vessel annotations are available. The first set by Adam Hoover ("ah") is
commonly used for training and testing. The second set by Valentina Kouznetsova
("vk") is typically used as a “human” baseline.

* Database references:

  * Original data: [STARE-2000]_
  * Split reference: [MANINIS-2016]_

Data specifications:

* Raw data input (on disk):

  * RGB images encoded in PPM format with resolution (HxW) = 605 x 700
  * Total samples: 397 (out of which only 20 are annotated for vessel
    segmentation)

* Output sample:

    * Image: Load raw PPM images with :py:mod:`PIL`, with auto-conversion to RGB.
    * Vessel annotations: Load annotations with :py:mod:`PIL`, with
      auto-conversion to model ``1`` with no dithering.
    * Eye fundus mask: Load mask with :py:mod:`PIL`, with
      auto-conversion to model ``1`` with no dithering.

Protocol ``ah`` (default baseline, with first, more detailed annotator)
includes 10 training samples and 10 test samples.  Protocol ``vk`` (second
annotator) includes the same samples but annotated by a second expert.

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
    """A specialized raw-data-loader for the Stare database."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

    def sample(self, sample: tuple[str, str, str | None]) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the database root folder,
            where to find the image to be loaded, and an integer, representing the
            sample label.

        Returns
        -------
            The sample representation.
        """

        image = to_tensor(PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB"))

        target = to_tensor(
            PIL.Image.open(self.datadir / sample[1]).convert(mode="1", dither=None)
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
    """STARE database for Vessel Segmentation.

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
