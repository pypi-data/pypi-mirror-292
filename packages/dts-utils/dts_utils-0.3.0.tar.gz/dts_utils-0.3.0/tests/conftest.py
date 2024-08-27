# SPDX-FileCopyrightText: 2023 - 2024 Ledger SAS
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

import pathlib
import dts_utils
import pytest


class Dts:
    def __init__(self):
        self.dts = dts_utils.Dts(pathlib.Path(__file__).parent.absolute() / "dts/sample.dts")


@pytest.fixture(scope="module")
def dts_file():
    return Dts()
