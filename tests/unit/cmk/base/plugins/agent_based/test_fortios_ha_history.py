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

from typing import Tuple

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from cmk.base.plugins.agent_based.fortios_ha_history import (
    Event,
    Section,
    check_fortios_ha_history,
    parse_fortios_ha_history,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [['{"http_method":"GET","revision":"2241696696257","results":{"start_time":1679574068,"last_change":1688979101,"history":[{"time":1696696257,"event":"member node01 lost heartbeat on hbdev port2"},{"time":1696691966,"event":"member node02 lost heartbeat on hbdev port1"}]},"vdom":"root","path":"system","name":"ha-history","action":"","status":"success","serial":"Serial01","version":"v7.0.12","build":6681}']],
            [Section(history=[Event(time="1696696257", event="member node01 lost heartbeat on hbdev port2"), Event(time="1696691966", event="member node02 lost heartbeat on hbdev port1")])],
        ),
    ],
)
def test_parse_fortios_ha_history(string_table, expected_section) -> None:
    assert parse_fortios_ha_history(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "event",
            [
                (Section(history=[Event(time="1696696257", event="member node01 lost heartbeat on hbdev port2"), Event(time="1696691966", event="member node02 lost heartbeat on hbdev port1")])),
            ],
            [
                (Result(state=State.OK, summary="Oct 07 2023 16:30:57: member node01 lost heartbeat on hbdev port2", details="Oct 07 2023 16:30:57: member node01 lost heartbeat on hbdev port2\nOct 07 2023 15:19:26: member node02 lost heartbeat on hbdev port1"),),
            ],
        ),
    ],
)
def test_check_fortios_ha_history(item: str, section: str, expected_check_result: Tuple) -> None:
    assert tuple(check_fortios_ha_history(item, section[0])) == expected_check_result[0]
