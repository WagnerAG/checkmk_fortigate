#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of  the  GNU General Public License  as published by
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

import json
from typing import Mapping

import pytest
from cmk.agent_based.v2 import Metric, Result, Service, State

from cmk_addons.plugins.fortios.agent_based.fortios_link_monitor import (
    LinkMonitor,
    check_fortios_link_monitor,
    discovery_fortios_link_monitor,
    parse_fortios_link_monitor,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [[json.dumps({"vdom": "root", "results": {"wan1": {"interface": "port1", "status": "up", "latency": 12.5, "jitter": 3.2, "packet-loss": 1.5}}})]],
            {"wan1 over port1": LinkMonitor(name="wan1", label="port1", state="alive", latency=12.5, jitter=3.2, packet_loss=1.5, vdom="root")},
        ),
        (
            [[json.dumps({"vdom": "root", "results": [{"name": "wan1", "children": [{"interface": "port1", "status": "down", "latency": 45.0, "jitter": 5.0, "packet-loss": 2.0}]}]})]],
            {"wan1 over port1": LinkMonitor(name="wan1", label="port1", state="dead", latency=45.0, jitter=5.0, packet_loss=2.0, vdom="root")},
        ),
        ([], None),
    ],
)
def test_parse_fortios_link_monitor(string_table: list[list[str]] | list[list], expected_section: Mapping[str, LinkMonitor] | None) -> None:
    assert parse_fortios_link_monitor(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_services",
    [
        ({"wan1 over port1": LinkMonitor(name="wan1", label="port1", state="alive", latency=12.5, jitter=3.2, packet_loss=1.5, vdom="root")}, [Service(item="wan1 over port1")]),
        ({}, []),
    ],
)
def test_discover_fortios_link_monitor(section: Mapping[str, LinkMonitor], expected_services: list[Service]) -> None:
    assert list(discovery_fortios_link_monitor(section)) == expected_services


@pytest.mark.parametrize(
    "item, section, params, expected_check_result",
    [
        (
            "wan1 over port1",
            {"wan1 over port1": LinkMonitor(name="wan1", label="port1", state="alive", latency=12.5, jitter=3.2, packet_loss=1.5, vdom="root")},
            {},
            [
                Result(state=State.OK, summary="Link monitor is alive, VDOM: root"),
                Result(state=State.OK, notice="Latency: 12.50 ms"),
                Metric("latency", 12.5, boundaries=(0.0, None)),
                Result(state=State.OK, notice="Jitter: 3.20 ms"),
                Metric("jitter", 3.2, boundaries=(0.0, None)),
                Result(state=State.OK, notice="Packet loss: 1.50%"),
                Metric("pl", 1.5, boundaries=(0.0, 100.0)),
            ],
        ),
        (
            "wan1 over port1",
            {"wan1 over port1": LinkMonitor(name="wan1", label="port1", state="dead", latency=12.5, jitter=3.2, packet_loss=1.5, vdom="root")},
            {},
            [
                Result(state=State.CRIT, summary="Link monitor is dead, VDOM: root"),
                Result(state=State.OK, notice="Latency: 12.50 ms"),
                Metric("latency", 12.5, boundaries=(0.0, None)),
                Result(state=State.OK, notice="Jitter: 3.20 ms"),
                Metric("jitter", 3.2, boundaries=(0.0, None)),
                Result(state=State.OK, notice="Packet loss: 1.50%"),
                Metric("pl", 1.5, boundaries=(0.0, 100.0)),
            ],
        ),
        (
            "wan1 over port1",
            {"wan1 over port1": LinkMonitor(name="wan1", label="port1", state="disabled", latency=12.5, jitter=3.2, packet_loss=1.5, vdom="root")},
            {},
            [
                Result(state=State.WARN, summary="Link monitor is disabled, VDOM: root"),
                Result(state=State.OK, notice="Latency: 12.50 ms"),
                Metric("latency", 12.5, boundaries=(0.0, None)),
                Result(state=State.OK, notice="Jitter: 3.20 ms"),
                Metric("jitter", 3.2, boundaries=(0.0, None)),
                Result(state=State.OK, notice="Packet loss: 1.50%"),
                Metric("pl", 1.5, boundaries=(0.0, 100.0)),
            ],
        ),
    ],
)
def test_check_fortios_link_monitor(
    item: str,
    section: Mapping[str, LinkMonitor],
    params: Mapping[str, object],
    expected_check_result: list[Result | Metric],
) -> None:
    assert list(check_fortios_link_monitor(item, params, section)) == expected_check_result
