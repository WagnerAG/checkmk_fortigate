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

from cmk.agent_based.v2 import Result, State
from cmk_addons.plugins.fortios.agent_based.fortios_ha_peer import (
    HACluster,
    HAPeer,
    check_fortios_ha_peer,
    parse_fortios_ha_peer,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"build": 3651, "http_method": "GET", "name": "ha-peer", "path": "system", "results": [{"hostname": "firewall01", "master": true, "primary": true, "priority": 100, "serial_no": "Serial01", "vcluster_id": 0}, {"hostname": "firewall02", "priority": 50, "serial_no": "Serial02", "vcluster_id": 0}], "serial": "Serial01", "status": "success", "vdom": "root", "version": "v7.6.5"}'
                ]
            ],
            HACluster(
                peers=[
                    HAPeer(
                        hostname="firewall01",
                        master=True,
                        primary=True,
                        priority=100,
                        serial_no="Serial01",
                        vcluster_id=0,
                    ),
                    HAPeer(
                        hostname="firewall02",
                        master=False,
                        primary=False,
                        priority=50,
                        serial_no="Serial02",
                        vcluster_id=0,
                    ),
                ]
            ),
        ),
    ],
)
def test_parse_fortios_ha_peer(string_table, expected_section) -> None:
    assert parse_fortios_ha_peer(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "firewall01",
            HACluster(
                peers=[
                    HAPeer(
                        hostname="firewall01",
                        master=True,
                        primary=True,
                        priority=100,
                        serial_no="Serial01",
                        vcluster_id=0,
                    ),
                    HAPeer(
                        hostname="firewall02",
                        master=False,
                        primary=False,
                        priority=50,
                        serial_no="Serial02",
                        vcluster_id=0,
                    ),
                ]
            ),
            Result(
                state=State.OK,
                summary=("Primary: firewall01, Node Serial: Serial01, Priority: 100, Cluster ID: 0, Secondary nodes: see details"),
                details=("Primary: firewall01, Node Serial: Serial01, Priority: 100, Cluster ID: 0\nSecondary: firewall02, Node Serial: Serial02, Priority: 50, Cluster ID: 0"),
            ),
        ),
        (
            "firewall02",
            HACluster(
                peers=[
                    HAPeer(
                        hostname="firewall01",
                        master=True,
                        primary=True,
                        priority=100,
                        serial_no="Serial01",
                        vcluster_id=0,
                    ),
                ],
            ),
            Result(
                state=State.WARN,
                summary=("Primary: firewall01, Node Serial: Serial01, Priority: 100, Cluster ID: 0, Secondary nodes: not found!"),
                details=("Primary: firewall01, Node Serial: Serial01, Priority: 100, Cluster ID: 0"),
            ),
        ),
    ],
)
def test_check_fortios_ha_peer(item: str, section: HACluster, expected_check_result: Result) -> None:
    results = tuple(check_fortios_ha_peer(item, section))
    assert len(results) == 1
    assert results[0] == expected_check_result
