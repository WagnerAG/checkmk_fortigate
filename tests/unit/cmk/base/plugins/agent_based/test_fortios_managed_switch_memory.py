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
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_managed_switch_health import CPU, POE, FortiosSwitchData, Memory, PerformanceStatus, TimeUnit, Uptime
from cmk.base.plugins.agent_based.fortios_managed_switch_memory import check_fortios_switch_memory

PerformanceStatus.update_forward_refs()


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            (FortiosSwitchData(performance_status=PerformanceStatus(cpu=CPU(idle=TimeUnit(unit="%", value=87), nice=TimeUnit(unit="%", value=0), system=TimeUnit(unit="%", value=12), user=TimeUnit(unit="%", value=1)), memory=Memory(used=TimeUnit(unit="%", value=36)), uptime=Uptime(days=TimeUnit(unit="days", value=113), hours=TimeUnit(unit="hours", value=5), minutes=TimeUnit(unit="minutes", value=16))), poe=POE(max_value=800, unit="watts", value=26.1))),
            [Result(state=State.OK, summary="Total Memory: 36%"), Metric("mem_used", 36, boundaries=(0, 100))],
        ),
    ],
)
def test_check_fortios_managed_switch_memory(section: FortiosSwitchData, expected_check_result) -> None:
    actual_check_result = list(check_fortios_switch_memory(section))
    assert actual_check_result == expected_check_result
