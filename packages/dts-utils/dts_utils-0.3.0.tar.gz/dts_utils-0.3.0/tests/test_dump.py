# SPDX-FileCopyrightText: 2023 - 2024 Ledger SAS
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

import dts_utils
import dts_utils.dump


def test_dump(dts_file):
    usart1_info = dts_utils.dump.dump(dts_file.dts, "usart1", True)
