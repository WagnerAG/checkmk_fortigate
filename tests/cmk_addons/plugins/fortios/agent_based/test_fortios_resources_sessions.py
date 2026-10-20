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

from typing import Dict

import pytest
from cmk.agent_based.v2 import Metric, Result, State

from cmk_addons.plugins.fortios.agent_based.fortios_resources import FortiResource, ResourceUsage, UsageSample
from cmk_addons.plugins.fortios.agent_based.fortios_resources_sessions import check_fortios_resources_sessions

DEFAULT_SESSION_LEVELS: Dict = {"session_levels": ("fixed", (5000, 10000))}


@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        (
            DEFAULT_SESSION_LEVELS,
            FortiResource(results=ResourceUsage(cpu=[UsageSample(current=25)], mem=[UsageSample(current=21)], session=[UsageSample(current=5000)])),
            [
                Result(state=State.OK, summary="Sessions"),
                Metric("active_sessions", 5000.0, levels=(5000, 10000)),
                Result(state=State.WARN, summary="Total: 5000.00 (warn/crit at 5000.00/10000.00)"),
                Metric("total_sessions", 5000.0, levels=(5000, 10000), boundaries=(0.0, None)),
            ],
        ),
    ],
)
def test_check_fortios_resources_sessions(params: Dict, section: FortiResource, expected_check_result) -> None:
    actual_check_result = list(check_fortios_resources_sessions(params, section))
    assert actual_check_result == expected_check_result
