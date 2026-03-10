#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# WAGNER AG
# Developer: opensource@wagner.ch

from typing import Any, Mapping

import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_device_info_inventory import DeviceInfo, ModelInfo
from cmk_addons.plugins.fortios.agent_based.fortios_system import check_fortios_system, discover_fortios_system

FULL_SECTION = {
    "Hostname01": DeviceInfo(
        serial="FGTSerialNumber",
        version="v7.2.7",
        build=1577,
        results=ModelInfo(hostname="Hostname01", model="FGT60F", model_name="FortiGate", model_number="60F"),
    )
}


@pytest.mark.parametrize(
    "section, expected_services",
    [
        (FULL_SECTION, [Service()]),
        ({}, []),
    ],
)
def test_discover_fortios_system(section: Mapping[str, DeviceInfo], expected_services: list[Service]) -> None:
    assert list(discover_fortios_system(section)) == expected_services


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            FULL_SECTION,
            [
                Result(state=State.OK, summary="Version v7.2.7 Build 1577", details="Model: FortiGate FGT60F, Hostname: Hostname01, Serial: FGTSerialNumber"),
                Metric("version_numeric", 70207),
                Metric("build_number", 1577),
            ],
        ),
        ({}, [Result(state=State.UNKNOWN, summary="No data received")]),
        (["invalid"], [Result(state=State.UNKNOWN, summary="Unexpected data format")]),
    ],
)
def test_check_fortios_system(section: Mapping[str, DeviceInfo] | list[Any], expected_check_result: list[Result | Metric]) -> None:
    assert list(check_fortios_system(section)) == expected_check_result