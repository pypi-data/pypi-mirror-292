# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tests for NIH CXR-14 dataset."""

import importlib

import pytest
from click.testing import CliRunner


def id_function(val):
    if isinstance(val, dict):
        return str(val)
    return repr(val)


@pytest.mark.parametrize(
    "split,lengths",
    [
        ("default.json.bz2", dict(train=98637, validation=6350, test=4054)),
        ("cardiomegaly.json", dict(train=40, validation=40)),
    ],
    ids=id_function,  # just changes how pytest prints it
)
def test_protocol_consistency(
    database_checkers,
    split: str,
    lengths: dict[str, int],
):
    from mednet.data.split import make_split

    database_checkers.check_split(
        make_split("mednet.config.classify.data.nih_cxr14", f"{split}"),
        lengths=lengths,
        prefixes=("images/000",),
        possible_labels=(0, 1),
    )


testdata = [
    ("default", "train", 14),
    ("default", "validation", 14),
    ("default", "test", 14),
    ("cardiomegaly", "train", 14),
    ("cardiomegaly", "validation", 14),
]


@pytest.mark.skip_if_rc_var_not_set("datadir.nih_cxr14")
def test_database_check():
    from mednet.scripts.database import check

    runner = CliRunner()
    result = runner.invoke(check, ["--limit=10", "nih-cxr14"])
    assert (
        result.exit_code == 0
    ), f"Exit code {result.exit_code} != 0 -- Output:\n{result.output}"


@pytest.mark.skip_if_rc_var_not_set("datadir.nih_cxr14")
@pytest.mark.parametrize("name,dataset,num_labels", testdata)
def test_loading(database_checkers, name: str, dataset: str, num_labels: int):
    datamodule = importlib.import_module(
        f".{name}", "mednet.config.classify.data.nih_cxr14"
    ).datamodule

    datamodule.model_transforms = []  # should be done before setup()
    datamodule.setup("predict")  # sets up all datasets

    loader = datamodule.predict_dataloader()[dataset]

    limit = 3  # limit load checking
    for batch in loader:
        if limit == 0:
            break
        database_checkers.check_loaded_batch(
            batch,
            batch_size=1,
            color_planes=1,
            prefixes=("images/000",),
            possible_labels=(0, 1),
            expected_num_labels=num_labels,
            expected_image_shape=(1, 1024, 1024),
            expected_meta_size=2,
        )
        limit -= 1


@pytest.mark.skip_if_rc_var_not_set("datadir.nih_cxr14")
def test_loaded_image_quality(database_checkers, datadir):
    reference_histogram_file = (
        datadir / "histograms/raw_data/histograms_nih_cxr14_default.json"
    )

    datamodule = importlib.import_module(
        ".default", "mednet.config.classify.data.nih_cxr14"
    ).datamodule

    datamodule.model_transforms = []
    datamodule.setup("predict")

    database_checkers.check_image_quality(datamodule, reference_histogram_file)
