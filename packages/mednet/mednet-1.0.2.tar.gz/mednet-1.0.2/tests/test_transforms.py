# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for transforms."""

import numpy
import PIL.Image
import torch
import torchvision.transforms.functional as F  # noqa: N812

from mednet.data.augmentations import ElasticDeformation
from mednet.models.transforms import crop_image_to_mask


def test_crop_mask():
    original_tensor_size = (3, 50, 100)
    original_mask_size = (1, 50, 100)
    slice_ = (slice(None), slice(10, 30), slice(50, 70))

    tensor = torch.rand(original_tensor_size)
    mask = torch.zeros(original_mask_size)
    mask[slice_] = 1

    cropped_tensor = crop_image_to_mask(tensor, mask)

    assert cropped_tensor.shape == (3, 20, 20)
    assert torch.all(cropped_tensor.eq(tensor[slice_]))


def test_elastic_deformation(datadir):
    # Get a raw sample without deformation
    data_file = str(datadir / "raw_without_elastic_deformation.png")
    raw_without_deformation = F.to_tensor(PIL.Image.open(data_file))

    # Elastic deforms the raw
    numpy.random.seed(seed=100)
    ed = ElasticDeformation()
    raw_deformed = ed(raw_without_deformation)

    # Get the same sample already deformed (with seed=100)
    data_file_2 = str(datadir / "raw_with_elastic_deformation.png")
    raw_2 = PIL.Image.open(data_file_2)

    # Compare both
    raw_deformed = (255 * numpy.asarray(raw_deformed)).astype(numpy.uint8)[
        0,
        :,
        :,
    ]
    raw_2 = numpy.asarray(raw_2)

    numpy.testing.assert_array_equal(raw_deformed, raw_2)
