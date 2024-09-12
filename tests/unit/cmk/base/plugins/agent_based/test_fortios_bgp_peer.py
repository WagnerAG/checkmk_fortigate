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
from cmk.base.plugins.agent_based.fortios_bgp_peer import (
    Peer,
    check_fortios_bgp_peer,
    parse_fortios_bgp_peer,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                ['{"action": "neighbors","build": "1639","http_method": "GET","name": "bgp","path": "router","results": [{"admin_status": "true","local_ip": "10.10.10.2","neighbor_ip": "10.110.0.2","remote_as": "12345","state": "Established","type": "ipv4"}],"serial": "Serial01","status": "success","vdom": "root","version": "v7.2.8"}'],
            ],
            [
                {"10.110.0.2": Peer(admin_status="true", local_ip="10.10.10.2", neighbor_ip="10.110.0.2", remote_as="12345", state="Established", type="ipv4")},
            ],
        ),
    ],
)
def test_parse_fortios_bgp_peer(string_table, expected_section) -> None:
    assert parse_fortios_bgp_peer(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "10.110.0.2",
            [
                ({"10.110.0.2": Peer(admin_status=False, local_ip="10.10.10.2", neighbor_ip="10.110.0.2", remote_as="12345", state="Disconnected", type="ipv4")}),
            ],
            [
                (Result(state=State.CRIT, summary="Peer state: Disconnected, Local IP: 10.10.10.2, Remote AS: 12345, Remote IP: 10.110.0.2"),),
            ],
        ),
        (
            "10.110.0.2",
            [
                ({"10.110.0.2": Peer(admin_status=True, local_ip="10.10.10.2", neighbor_ip="10.110.0.2", remote_as="12345", state="Established", type="ipv4")}),
            ],
            [
                (Result(state=State.OK, summary="Peer state: Established, Local IP: 10.10.10.2, Remote AS: 12345, Remote IP: 10.110.0.2"),),
            ],
        ),
        (
            "10.110.0.2",
            [
                ({"10.110.0.2": Peer(admin_status=True, local_ip="0.0.0.0", neighbor_ip="10.110.0.2", remote_as="12345", state="Idle", type="ipv4")}),
            ],
            [
                (Result(state=State.CRIT, summary="Peer state: Idle, Local IP: 0.0.0.0, Remote AS: 12345, Remote IP: 10.110.0.2"),),
            ],
        ),
    ],
)
def test_check_fortios_bgp_peer_item(item: str, section: str, expected_check_result: Tuple) -> None:
    assert tuple(check_fortios_bgp_peer(item, section[0])) == expected_check_result[0]
