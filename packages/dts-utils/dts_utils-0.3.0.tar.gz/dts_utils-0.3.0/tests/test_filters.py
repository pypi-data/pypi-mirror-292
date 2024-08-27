# SPDX-FileCopyrightText: 2023 - 2024 Ledger SAS
#
# SPDX-License-Identifier: Apache-2.0

# flake8: noqa

import dts_utils
import dts_utils.filters


def test_filter_enabled(dts_file):
    pinctrl_list = dts_utils.filters.f_peripherals(dts_file.dts.soc.pinctrl)
    enabled_gpios = dts_utils.filters.f_enabled(pinctrl_list)
    assert len(enabled_gpios) == 7


def test_filter_enabled_exceptions(dts_file):
    try:
        enabled_gpios = dts_utils.filters.f_enabled(dts_file.dts)
        assert False
    except dts_utils.exceptions.InvalidTemplateValueType:
        assert True


def test_filter_owner(dts_file):
    i2c1 = dts_file.dts.i2c1
    assert dts_utils.filters.f_owner(i2c1) == 0xBABE


def test_filter_owner_exceptions(dts_file):
    try:
        enabled_gpios = dts_utils.filters.f_owner(dts_file.dts)
        assert False
    except dts_utils.exceptions.InvalidTemplateValueType:
        assert True


def test_filter_has_property(dts_file):
    i2c1 = dts_file.dts.i2c1
    assert dts_utils.filters.f_has_property(i2c1, "outpost,owner")


def test_filter_has_property_exception(dts_file):
    try:
        dts_utils.filters.f_has_property(dts_file.dts, "outpost,owner")
        assert False
    except dts_utils.exceptions.InvalidTemplateValueType:
        assert True


def test_filter_with_property(dts_file):
    dev_list = dts_utils.filters.f_peripherals(dts_file.dts.root)
    assert len(dts_utils.filters.f_with_property(dev_list, "outpost,owner")) == 1


def test_filter_with_property_exception(dts_file):
    try:
        dts_utils.filters.f_with_property(dts_file.dts, "outpost,owner")
        assert False
    except dts_utils.exceptions.InvalidTemplateValueType:
        assert True
    try:
        dts_utils.filters.f_with_property(dts_file.dts.usart1, "outpost,owner")
        assert False
    except dts_utils.exceptions.InvalidTemplateValueType:
        assert True
