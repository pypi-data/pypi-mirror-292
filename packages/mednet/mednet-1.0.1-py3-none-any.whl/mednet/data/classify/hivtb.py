# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""HIV-TB dataset for computer-aided diagnosis (only BMP files).

This databases contain only the tuberculosis final diagnosis (0 or 1) and come
from HIV infected patients.

* Database reference: [HIV-TB-2019]_

.. important:: **Raw data organization**

    The HIV-TB base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least the directory
    ``HIV-TB/HIV-TB_Algorithm_study_X-rays`` with all BMP and JPEG images.

Data specifications:

* Raw data input (on disk):

  * BMP (BMP3) and JPEG grayscale images encoded as 8-bit RGB, with
    varying resolution (most images being 2048 x 2500 pixels or 2500 x 2048
    pixels, but not all).
  * Total samples: 243

* Output image:

  * Transforms:

    * Load raw BMP or JPEG with :py:mod:`PIL`, with auto-conversion to
      grayscale
    * Remove black borders
    * Convert to torch tensor

* Final specifications

  * Grayscale, encoded as a single plane tensor, 32-bit floats, with varying
    resolution depending on input.
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
    """A specialized raw-data-loader for the HIV-TB dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    def __init__(self):
        self.datadir = pathlib.Path(
            load_rc().get(
                CONFIGURATION_KEY_DATADIR,
                os.path.realpath(os.curdir),
            ),
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

        image = PIL.Image.open(self.datadir / sample[0]).convert("L")
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
    """HIV-TB dataset for computer-aided diagnosis (only BMP files).

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
