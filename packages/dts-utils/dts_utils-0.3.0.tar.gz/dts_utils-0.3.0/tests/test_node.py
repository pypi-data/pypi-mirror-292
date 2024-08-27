# SPDX-FileCopyrightText: 2023 - 2024 Ledger SAS
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

import dts_utils


def test_node_id(dts_file):
    usart1 = dts_file.dts.usart1
    assert usart1.label == "usart1"
    assert usart1.name == "serial@40013800"
