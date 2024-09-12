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

from datetime import datetime, timedelta
from typing import Dict, Tuple
from unittest.mock import patch

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_ipsec import (
    FortiIPSec,
    check_fortios_ipsec,
    parse_fortios_ipsec,
)

IPSEC_SECTION: dict = {
    "P1_TEST": FortiIPSec(
        name="P1_TEST",
        proxyid=[
            {
                "proxy_src": [{"subnet": "10.10.10.0-10.10.10.255", "port": 0, "protocol": 0, "protocol_name": ""}],
                "proxy_dst": [{"subnet": "172.16.0.0-172.16.0.63", "port": 0, "protocol": 0, "protocol_name": ""}],
                "status": "up",
                "p2name": "P2_TEST",
                "p2serial": 5,
                "expire": 3105,
                "incoming_bytes": 1847216,
                "outgoing_bytes": 14422894,
            },
            {
                "proxy_src": [{"subnet": "0.0.0.0/0.0.0.0", "port": 0, "protocol": 0, "protocol_name": ""}],
                "proxy_dst": [{"subnet": "0.0.0.0/0.0.0.0", "port": 0, "protocol": 0, "protocol_name": ""}],
                "status": "down",
                "p2name": "P2_TEST",
                "p2serial": 1,
            },
        ],
        comments="",
        connection_count=638,
        creation_time=8975812,
        type="automatic",
        incoming_bytes=4888573499940,
        outgoing_bytes=308984509918,
        rgwy="10.20.30.10",
        tun_id="10.20.30.10",
        tun_id6="::10.20.30.10",
        wizard_type="custom",
    )
}


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '[{"http_method":"GET","results":[{"proxyid":[{"proxy_src":[{"subnet":"10.10.10.0-10.10.10.255","port":0,"protocol":0,"protocol_name":""}],"proxy_dst":[{"subnet":"172.16.0.0-172.16.0.63","port":0,"protocol":0,"protocol_name":""}],"status":"up","p2name":"P2_TEST","p2serial":5,"expire":3105,"incoming_bytes":1847216,"outgoing_bytes":14422894},{"proxy_src":[{"subnet":"0.0.0.0\\/0.0.0.0","port":0,"protocol":0,"protocol_name":""}],"proxy_dst":[{"subnet":"0.0.0.0\\/0.0.0.0","port":0,"protocol":0,"protocol_name":""}],"status":"down","p2name":"P2_TEST","p2serial":1}],"name":"P1_TEST","comments":"","wizard-type":"custom","connection_count":638,"creation_time":8975812,"type":"automatic","incoming_bytes":4888573499940,"outgoing_bytes":308984509918,"rgwy":"10.20.30.10","tun_id":"10.20.30.10","tun_id6":"::10.20.30.10"}],"vdom":"VDOM01","path":"vpn","name":"ipsec","action":"","status":"success","serial":"Serial01","version":"v7.0.12","build":6681}]'
                ]
            ],
            IPSEC_SECTION,
        ),
    ],
)
def test_parse_fortios_ipsec(string_table, expected_section) -> None:
    assert parse_fortios_ipsec(string_table) == expected_section


DEFAULT_PARAMS: Dict = {
    "fortios_tunnels_ignore": [],
    "fortios_tunnels_src_subnet_ignore": [],
    "fortios_tunnels_dst_subnet_ignore": [],
}


@pytest.mark.parametrize(
    "item, section, params, expected_check_result",
    [
        (
            "P1_TEST",
            IPSEC_SECTION,
            DEFAULT_PARAMS,
            [
                Result(state=State.CRIT, summary='Type: automatic', details="Tunnels up: [P2_TEST: ['172.16.0.0-172.16.0.63']], \n\n                Tunnels down: [P2_TEST: ['0.0.0.0/0.0.0.0']], \n\n                Tunnels ignored by name: [], \n\n                Tunnels ignored by destination subnet: [], \n\n                "),
                Result(state=State.OK, summary="Total: 2.00"),
                Metric("ipsec_total", 2.0),
                Metric("total_tunnels", 2),
                Result(state=State.OK, summary="Up: 1.00"),
                Metric("ipsec_up", 1.0),
            ],
        ),
    ],
)
def test_check_fortios_ipsec(item: str, section: str, params: dict, expected_check_result: Tuple) -> None:
    with patch("cmk.base.plugins.agent_based.fortios_ipsec.get_value_store") as mock_get:
        timestamp = int((datetime.now() - timedelta(minutes=2)).timestamp())
        mock_get.return_value = {"if_in_bps": (timestamp, 0.0), "if_out_bps": (timestamp, 0.0)}
        check_results = list(check_fortios_ipsec(item, params, section))
        for result, expected in zip(check_results, expected_check_result):
            assert result == expected
