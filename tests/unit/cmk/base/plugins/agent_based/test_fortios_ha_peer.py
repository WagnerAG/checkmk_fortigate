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
from cmk.base.plugins.agent_based.fortios_ha_peer import (
    Peer,
    check_fortios_ha_peer,
    parse_fortios_ha_peer,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [['{"action": "", "build": 1639, "http_method": "GET", "name": "ha-peer", "path": "system", "results": [{"hostname": "ffw01", "priority": 200, "serial_no": "Serial01", "vcluster_id": 0}, {"hostname": "ffw02", "priority": 180, "serial_no": "Serial02", "vcluster_id": 0}], "serial": "Serial00", "status": "success", "vdom": "root", "version": "v7.2.8"}']],
            [{"ffw01": Peer(serial_no="Serial01", vcluster_id=0, priority=200, hostname="ffw01", status="success"), "ffw02": Peer(serial_no="Serial02", vcluster_id=0, priority=180, hostname="ffw02", status="success")}],
        ),
    ],
)
def test_parse_fortios_ha_peer(string_table, expected_section) -> None:
    assert parse_fortios_ha_peer(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "ffw01",
            [
                ({"ffw01": Peer(serial_no="Serial01", vcluster_id=0, priority=200, hostname="ffw01", status="failing")}),
            ],
            [
                (Result(state=State.CRIT, summary="Cluster status: failing, Cluster ID: 0, Priority: 200, Node Serial: Serial01"),),
            ],
        ),
        (
            "ffw01",
            [
                ({"ffw01": Peer(serial_no="Serial01", vcluster_id=0, priority=200, hostname="ffw01", status="success")}),
            ],
            [
                (Result(state=State.OK, summary="Cluster status: success, Cluster ID: 0, Priority: 200, Node Serial: Serial01"),),
            ],
        ),
        (
            "ffw02",
            [
                ({"ffw02": Peer(serial_no="Serial02", vcluster_id=0, priority=180, hostname="ffw02", status="success")}),
            ],
            [
                (Result(state=State.OK, summary="Cluster status: success, Cluster ID: 0, Priority: 180, Node Serial: Serial02"),),
            ],
        ),
    ],
)
def test_check_fortios_ha_peer_item(item: str, section: str, expected_check_result: Tuple) -> None:
    assert tuple(check_fortios_ha_peer(item, section[0])) == expected_check_result[0]
