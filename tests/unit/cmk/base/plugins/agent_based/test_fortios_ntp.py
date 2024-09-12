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

from typing import Mapping

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_ntp import (
    DEFAULT_OFFSET_LEVELS,
    FortiNTP,
    check_fortios_ntp,
    parse_fortios_ntp,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"action": "status", "build": 1575, "http_method": "GET", "name": "ntp", "path": "system", '
                    '"results": [{"expires": 266, "ip": "82.197.188.130", "reachable": true, "server": "ch.pool.ntp.org"}, '
                    '{"expires": 266, "ip": "212.51.144.46", "reachable": true, "server": "ch.pool.ntp.org"}, '
                    '{"expires": 266, "ip": "62.12.167.109", "reachable": true, "server": "ch.pool.ntp.org"}, '
                    '{"expires": 3, "ip": "unresolved", "reachable": false, "server": "ch.pool.ntp.org"}, '
                    '{"delay": 3.6773681640625, "dispersion": 20.44677734375, "expires": 266, "ip": "130.60.204.10", '
                    '"offset": 11.742691040039062, "peer_dispersion": 535, "reachable": true, "reftime": 1706867483, '
                    '"selected": true, "server": "ch.pool.ntp.org", "stratum": 2, "version": 4}]}'
                ]
            ],
            {"ch.pool.ntp.org": FortiNTP(server="ch.pool.ntp.org", reachable=True, offset=11.742691040039062, ip="130.60.204.10", stratum=2, selected=True)},
        ),
        (
            [[]],
            None,
        ),
    ],
)
def test_parse_fortios_ntp(string_table: list[list[str]] | list[list], expected_section: dict[str, FortiNTP] | None) -> None:
    assert parse_fortios_ntp(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            {"ch.pool.ntp.org": FortiNTP(server="ch.pool.ntp.org", reachable=True, stratum=2, ip="156.106.214.52", offset=-1.0837003707885743, selected=True)},
            [
                Result(state=State.OK, summary="Server: ch.pool.ntp.org, IP: 156.106.214.52, Selected: True"),
                Result(state=State.OK, summary="Time offset: -1.1 ms"),
                Metric('time_offset', -0.0010837003707885745, levels=(0.2, 0.5)),
                Result(state=State.OK, summary="Stratum: 2"),
            ],
        ),
        (
            {"ch.pool.ntp.org": FortiNTP(server="ch.pool.ntp.org", reachable=True, stratum=4, ip="156.106.214.52", offset=408.37003707885743, selected=True)},
            [
                Result(state=State.OK, summary="Server: ch.pool.ntp.org, IP: 156.106.214.52, Selected: True"),
                Result(state=State.WARN, summary="Time offset: 408.4 ms (warn/crit at 200.0 ms/500.0 ms)"),
                Metric('time_offset', 0.40837003707885744, levels=(0.2, 0.5)),
                Result(state=State.CRIT, summary="Stratum: 4 (warn/crit at 4/4)"),
            ],
        ),
        (
            {"ch.pool.ntp.org": FortiNTP(server="li.pool.ntp.org", reachable=True, stratum=5, ip="185.34.151.142", offset=-501.92375834025, selected=True)},
            [
                Result(state=State.OK, summary="Server: li.pool.ntp.org, IP: 185.34.151.142, Selected: True"),
                Result(state=State.CRIT, summary="Time offset: -501.9 ms (warn/crit below -200.0 ms/-500.0 ms)"),
                Metric('time_offset', -0.50192375834025, levels=(0.2, 0.5)),
                Result(state=State.CRIT, summary="Stratum: 5 (warn/crit at 4/4)"),
            ],
        ),
    ],
)
def test_check_fortios_ntp(section: Mapping[str, FortiNTP], expected_check_result: list) -> None:
    actual_check_result = list(check_fortios_ntp(DEFAULT_OFFSET_LEVELS, section))
    assert actual_check_result == expected_check_result
