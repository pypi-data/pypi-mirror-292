# SPDX-FileCopyrightText: 2023 - 2024 Ledger SAS
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

import dts_utils


def test_socload(dts_file):
    soc = dts_file.dts.soc
    assert soc != None
