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

import pytest
from cmk.base.plugins.agent_based.fortios_device_info_inventory import (
    ModelInfo,
    DeviceInfo,
    parse_fortios_device_info,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"action": "", "build": 9876, "http_method": "GET", "name": "status", "path": "system", "results": {"hostname": "Hostname01", "log_disk_status": "not_available", "model": "FGT60F", "model_name": "FortiGate", "model_number": "60F"}, "serial": "FGTSerialNumber", "status": "success", "vdom": "root", "version": "v7.x.y"}'
                ]
            ],
            [
                {
                    "Hostname01": DeviceInfo(
                        serial="FGTSerialNumber",
                        version="v7.x.y",
                        build=9876,
                        results=ModelInfo(
                            hostname="Hostname01",
                            model="FGT60F",
                            model_name="FortiGate",
                            model_number="60F",
                        ),
                    )
                }
            ],
        ),
    ],
)
def test_parse_fortios_device_info(string_table, expected_section) -> None:
    assert parse_fortios_device_info(string_table) == expected_section[0]
