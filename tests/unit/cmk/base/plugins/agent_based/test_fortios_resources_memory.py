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
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_resources import FortiResource, Resource, ResourceResult, Session
from cmk.base.plugins.agent_based.fortios_resources_memory import (
    check_fortios_resources_memory,
)

DEFAULT_MEMORY_LEVELS: Dict = {"memory_levels": (70.0, 80.0)}


@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        (
            DEFAULT_MEMORY_LEVELS,
            (FortiResource(vdoms=[ResourceResult(vdom="root", results=Resource(cpu=25, memory=21, session=Session(current_usage=5000)))], total_cpu=25, total_memory=25, total_sessions=5000)),
            [
                Result(state=State.OK, summary="Total usage"),
                Metric("memory_util", 21.0, levels=(70.0, 80.0), boundaries=(0, 100)),
                Result(state=State.OK, summary="21.00%"),
                Metric("memory_util", 21.0, levels=(70.0, 80.0), boundaries=(0, 100)),
            ],
        ),
    ],
)
def test_check_fortios_resources_memory(params: Dict, section: FortiResource, expected_check_result) -> None:
    actual_check_result = list(check_fortios_resources_memory(params, section))
    assert actual_check_result == expected_check_result
