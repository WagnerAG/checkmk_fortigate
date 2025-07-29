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

import time
from typing import Tuple

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_uptime import (
    Uptime,
    check_fortios_uptime,
    parse_fortios_uptime,
)
from freezegun import freeze_time
from unittest.mock import patch


@patch("cmk.base.plugins.agent_based.fortios_uptime.time.time", return_value=1720183649)
def test_parse_fortios_uptime(mock_time) -> None:
    string_table = [[
        '{"http_method":"GET", "results": {'
        '"snapshot_utc_time":1712050417000, '
        '"utc_last_reboot":1687436424000, '
        '"time_zone_offset":-120}, '
        '"serial":"Serial01", "hostname": "ffw01"}'
    ]]

    parsed = parse_fortios_uptime(string_table)

    assert parsed.utc_last_reboot == 1687436424
    assert parsed.snapshot_utc_time == 1712050417
    assert parsed.uptime == 1720183649 - 1687436424  # = 66352525

@freeze_time("2024-07-05 15:27:29")
@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            Uptime(hostname="ffw01", utc_last_reboot=1687436424000, snapshot_utc_time=1712050417000),
            [
                Result(state=State.OK, summary="Up since: 2023-06-22 12:20:24 UTC, Uptime: 1 year 14 days"),
                Metric("uptime", int(time.time() - 1687436424)),
            ],
        ),
    ],
)
def test_check_fortios_uptime(section: Uptime, expected_check_result: Tuple) -> None:
    assert list(check_fortios_uptime(section)) == expected_check_result
