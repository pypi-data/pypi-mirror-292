# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""RIM-ONE r3 (training set) for cup segmentation.

The dataset contains 159 stereo eye fundus images with a resolution of 2144 x
1424. The right part of the stereo image is disregarded. Two sets of
ground-truths for optic disc and optic cup are available. The first set is
commonly used for training and testing. The second set acts as a “human”
baseline.  A third set, composed of annotation averages may also be used for
training and evaluation purposes.

* Reference: [RIMONER3-2015]_
* Original resolution (height x width): 1424 x 1072
* Split reference: [MANINIS-2016]_
* Protocols ``optic-disc-exp1``, ``optic-cup-exp1``, ``optic-disc-exp2``,
  ``optic-cup-exp2``, ``optic-disc-avg`` and ``optic-cup-avg``
* Training: 99
* Test: 60

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources
import importlib.resources.abc
import os
import pathlib

import PIL.Image
from torchvision import tv_tensors
from torchvision.transforms.functional import crop, to_tensor

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
    """A specialized raw-data-loader for the rimoner3 dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir))
        )

    def crop_stereo_image(self, image):
        return crop(image, 0, 0, 1424, 1072)

    def sample(self, sample: tuple[str, str, str | None]) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing the
            sample label.

        Returns
        -------
            The sample representation.
        """

        image = to_tensor(
            self.crop_stereo_image(
                PIL.Image.open(self.datadir / sample[0]).convert(mode="RGB")
            )
        )
        target = to_tensor(
            self.crop_stereo_image(
                PIL.Image.open(self.datadir / sample[1]).convert(mode="1", dither=None)
            )
        )

        assert sample[2] is not None
        mask_path = (
            importlib.resources.files(__package__) / "masks" / DATABASE_SLUG / sample[2]
        )
        with importlib.resources.as_file(mask_path) as path:
            mask = to_tensor(
                self.crop_stereo_image(
                    PIL.Image.open(path).convert(mode="1", dither=None)
                )
            )

        image = tv_tensors.Image(image)
        target = tv_tensors.Mask(target)
        mask = tv_tensors.Mask(mask)

        return dict(image=image, target=target, mask=mask), dict(name=sample[0])  # type: ignore[arg-type]


class DataModule(CachingDataModule):
    """RIM-ONE r3 (training set) for cup segmentation.

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
