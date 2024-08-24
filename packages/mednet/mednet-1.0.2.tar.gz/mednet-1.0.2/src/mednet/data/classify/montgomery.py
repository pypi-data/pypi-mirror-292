# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Montgomery DataModule for TB detection.

The standard digital image database for Tuberculosis was created by the
National Library of Medicine, Maryland, USA in collaboration with Shenzhen No.3
People’s Hospital, Guangdong Medical College, Shenzhen, China.

* Database references: [MONTGOMERY-SHENZHEN-2014]_,

Data specifications:

* Raw data input (on disk):

  * PNG images 8 bit grayscale issued from digital radiography machines
  * Original resolution (height x width or width x height): 4020x4892 px or
    4892x4020 px
  * Samples: 138 images and associated labels

* Output image:

  * Transforms:

    * Load raw PNG with :py:mod:`PIL`
    * Remove black borders
    * Convert to torch tensor

  * Final specifications

    * Grayscale, encoded as a single plane tensor, 32-bit floats,
      square at most 4020 x 4020 pixels
    * Labels: 0 (healthy), 1 (active tuberculosis)

This module contains the base declaration of common data modules and raw-data
loaders for this database. All configured splits inherit from this definition.
"""

import importlib.resources.abc
import os
import pathlib
import typing

import PIL.Image
from torchvision import tv_tensors
from torchvision.transforms.functional import to_tensor

from ...utils.rc import load_rc
from ..datamodule import CachingDataModule
from ..image_utils import remove_black_borders
from ..split import JSONDatabaseSplit
from .typing import ClassificationRawDataLoader, Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""


class RawDataLoader(ClassificationRawDataLoader):
    """A specialized raw-data-loader for the Montgomery dataset.

    Parameters
    ----------
    config_variable
        Key to search for in the configuration file for the root directory of
        this database.
    """

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    # config_variable: required so this loader can be used for the small
    # version of the Montgomery database as well.
    def __init__(self, config_variable: str = CONFIGURATION_KEY_DATADIR):
        self.datadir = pathlib.Path(
            load_rc().get(config_variable, os.path.realpath(os.curdir)),
        )

    def sample(self, sample: tuple[str, int, typing.Any | None]) -> Sample:
        """Load a single image sample from the disk.

        Parameters
        ----------
        sample
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
            The sample representation.
        """

        # N.B.: Montgomery images are encoded as grayscale PNGs, so no need to
        # convert them again with Image.convert("L").
        image = PIL.Image.open(self.datadir / sample[0])
        image, _ = remove_black_borders(image)
        image = tv_tensors.Image(to_tensor(image))

        # use the code below to view generated images
        # from torchvision.transforms.functional import to_pil_image
        # to_pil_image(tensor).show()
        # __import__("pdb").set_trace()

        return dict(image=image), dict(target=sample[1], name=sample[0])  # type: ignore[arg-type]

    def target(self, k: typing.Any) -> int | list[int]:
        """Load a single image sample target from the disk.

        Parameters
        ----------
        k
            A tuple containing the path suffix, within the dataset root folder,
            where to find the image to be loaded, and an integer, representing
            the sample target.

        Returns
        -------
        int
            The integer target associated with the sample.
        """

        return k[1]


class DataModule(CachingDataModule):
    """Montgomery DataModule for TB detection.

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
            task="classification",
        )
