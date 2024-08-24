# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Definition of types related to models used in classification tasks."""

import typing

BinaryPrediction: typing.TypeAlias = tuple[str, int, float]
"""The sample name, the target, and the predicted value."""

MultiClassPrediction: typing.TypeAlias = tuple[
    str,
    typing.Sequence[int],
    typing.Sequence[float],
]
"""The sample name, the target, and the predicted value."""

BinaryPredictionSplit: typing.TypeAlias = typing.Mapping[
    str,
    typing.Sequence[BinaryPrediction],
]
"""A series of predictions for different database splits."""

MultiClassPredictionSplit: typing.TypeAlias = typing.Mapping[
    str,
    typing.Sequence[MultiClassPrediction],
]
"""A series of predictions for different database splits."""

SaliencyMapAlgorithm: typing.TypeAlias = typing.Literal[
    "ablationcam",
    "eigencam",
    "eigengradcam",
    "fullgrad",
    "gradcam",
    "gradcamelementwise",
    "gradcam++",
    "gradcamplusplus",
    "hirescam",
    "layercam",
    "randomcam",
    "scorecam",
    "xgradcam",
]
"""Supported saliency map algorithms."""
