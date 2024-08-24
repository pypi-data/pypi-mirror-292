# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""NIH CXR14 (relabeled) DataModule for computer-aided diagnosis.

This dataset was extracted from the clinical PACS database at the National
Institutes of Health Clinical Center (USA) and represents 60% of all their
radiographs. It contains labels for 14 common radiological signs in this order:
cardiomegaly, emphysema, effusion, hernia, infiltration, mass, nodule,
atelectasis, pneumothorax, pleural thickening, pneumonia, fibrosis, edema and
consolidation. This is the relabeled version created in the CheXNeXt study.

* Database references:

  * Original data: [NIH-CXR14-2017]_
  * Labels and split references: [CHEXNEXT-2018]_

.. important:: **Raw data organization**

    The NIH_CXR14_re_ base datadir, which you should configure following the
    :ref:`mednet.setup` instructions, must contain at least the directory
    "images/" with all the images of the database.

    The labels from [CHEXNEXT-2018]_ are already incorporated in this library
    and do **not** need to be re-downloaded.

    The flag ``idiap_folder_structure`` makes the loader search for files
    named, e.g. ``images/00030621_006.png``, as
    ``images/00030/00030621_006.png``.

* Raw data input (on disk):

  * PNG RGB 8-bit depth images
  * Resolution: 1024 x 1024 pixels
  * Total samples available: 109'041

* Output image:

  * Transforms:

    * Load raw PNG with :py:mod:`PIL`, with auto-conversion to grayscale
    * Convert to torch tensor

  * Final specifications:

    * RGB, encoded as a 3-plane tensor, 32-bit floats, square
      (1024x1024 px)
    * Labels in order:

      * cardiomegaly
      * emphysema
      * effusion
      * hernia
      * infiltration
      * mass
      * nodule
      * atelectasis
      * pneumothorax
      * pleural thickening
      * pneumonia
      * fibrosis
      * edema
      * consolidation

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
from ..split import JSONDatabaseSplit
from .typing import ClassificationRawDataLoader, Sample

DATABASE_SLUG = __name__.rsplit(".", 1)[-1]
"""Pythonic name of this database."""

CONFIGURATION_KEY_DATADIR = "datadir." + DATABASE_SLUG
"""Key to search for in the configuration file for the root directory of this
database."""

CONFIGURATION_KEY_IDIAP_FILESTRUCTURE = DATABASE_SLUG + ".idiap_folder_structure"
"""Key to search for in the configuration file indicating if the loader should
use standard or idiap-based file organisation structure.

It causes the internal loader to search for files in a slightly
different folder structure, that was adapted to Idiap's requirements
(number of files per folder to be less than 10k).
"""


class RawDataLoader(ClassificationRawDataLoader):
    """A specialized raw-data-loader for the NIH CXR-14 dataset."""

    datadir: pathlib.Path
    """This variable contains the base directory where the database raw data is
    stored."""

    idiap_file_organisation: bool
    """If should use the Idiap's filesystem organisation when looking up data.

    This variable will be ``True``, if the user has set the configuration
    parameter ``nih_cxr14.idiap_file_organisation`` in the global configuration
    file.  It will cause internal loader to search for files in a slightly
    different folder structure, that was adapted to Idiap's requirements
    (number of files per folder to be less than 10k).
    """

    def __init__(self):
        rc = load_rc()
        self.datadir = pathlib.Path(
            rc.get(CONFIGURATION_KEY_DATADIR, os.path.realpath(os.curdir)),
        )
        self.idiap_file_organisation = rc.get(
            CONFIGURATION_KEY_IDIAP_FILESTRUCTURE,
            False,
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

        file_path = pathlib.Path(sample[0])  # default
        if self.idiap_file_organisation:
            # for folder lookup efficiency, data is split into subfolders
            # each original file is on the subfolder `f[:5]/f`, where f
            # is the original file basename
            file_path = pathlib.Path(
                file_path.parent / file_path.name[:5] / file_path.name
            )

        # N.B.: some NIH CXR-14 images are encoded as color PNGs with an alpha
        # channel.  Most, are grayscale PNGs
        image = PIL.Image.open(self.datadir / file_path)
        image = image.convert("L")  # required for some images
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
            where to find the image to be loaded, and an integer, representing the
            sample target.

        Returns
        -------
        list[int]
            The integer targets associated with the sample.
        """

        return k[1]


class DataModule(CachingDataModule):
    """NIH CXR14 (relabeled) DataModule for computer-aided diagnosis.

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
