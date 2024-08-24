# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Defines most common types used in code."""

import typing

Checkpoint: typing.TypeAlias = typing.MutableMapping[str, typing.Any]
"""Definition of a lightning checkpoint."""
