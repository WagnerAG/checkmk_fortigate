#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from typing import Mapping, Tuple
from unittest.mock import patch

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from cmk.base.plugins.agent_based.fortios_sslvpn import Session, SSLVPNData, Subsession, check_fortios_sslvpn, parse_fortios_sslvpn


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '[{"action":"","build":1577,"http_method":"GET","name":"ssl","path":"vpn","results":[],"serial":"Serial01","status":"success","vdom":"VDOM1","version":"v7.2.x"},{"action":"","build":1577,"http_method":"GET","name":"ssl","path":"vpn","results":[{"index":0,"user_name":"user01","remote_host":"10.20.30.15","last_login_timestamp":1712838684,"two_factor_auth":false,"interface":"wan1","duration":177,"subsessions":[{"index":1,"parent_index":0,"mode":"Tunnel","type":"Unknown","aip":"10.10.10.100","in_bytes":10,"out_bytes":100,"desthost":""}],"subsession_type":"Unknown","subsession_desc":"aip:10.10.10.100"},{"index":0,"user_name":"user02","remote_host":"10.10.20.30","last_login_timestamp":1712938684,"two_factor_auth":false,"interface":"wan1","duration":190,"subsessions":[{"index":1,"parent_index":0,"mode":"Tunnel","type":"Unknown","aip":"10.10.1.110","in_bytes":20,"out_bytes":200,"desthost":""}],"subsession_type":"Unknown","subsession_desc":"aip:10.10.1.110"},{"index":0,"user_name":"user03","remote_host":"10.10.20.30","last_login_timestamp":1712938614,"two_factor_auth":false,"interface":"wan1","duration":1990,"subsessions":[{"index":1,"parent_index":0,"mode":"Tunnel","type":"Unknown","aip":"10.10.1.111","in_bytes":1000,"out_bytes":2000,"desthost":""}],"subsession_type":"Unknown","subsession_desc":"aip:10.10.10.111"}],"serial":"Serial01","status":"success","vdom":"root","version":"v7.2.x"}]'
                ]
            ],
            {
                "VDOM1": SSLVPNData(results=[], vdom="VDOM1", total_users=0, total_tunnels=0, connected_users="", if_in_bps=0, if_out_bps=0),
                "root": SSLVPNData(results=[Session(index=0, user_name="user01", remote_host="10.20.30.15", duration=177, subsessions=[Subsession(index=1, parent_index=0, mode="Tunnel", type="Unknown", aip="10.10.10.100", in_bytes=10, out_bytes=100, desthost="")], total_websessions=0, total_tunnels=0), Session(index=0, user_name="user02", remote_host="10.10.20.30", duration=190, subsessions=[Subsession(index=1, parent_index=0, mode="Tunnel", type="Unknown", aip="10.10.1.110", in_bytes=20, out_bytes=200, desthost="")], total_websessions=0, total_tunnels=0), Session(index=0, user_name="user03", remote_host="10.10.20.30", duration=1990, subsessions=[Subsession(index=1, parent_index=0, mode="Tunnel", type="Unknown", aip="10.10.1.111", in_bytes=1000, out_bytes=2000, desthost="")], total_websessions=0, total_tunnels=0)], vdom="root", total_users=3, total_tunnels=3, connected_users="user01, user02, user03", if_in_bps=1030, if_out_bps=2300),
            },
        ),
    ],
)
def test_parse_fortios_sslvpn(string_table, expected_section) -> None:
    assert parse_fortios_sslvpn(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "VDOM1",
            {
                "VDOM1": SSLVPNData(results=[], vdom="VDOM1", total_users=0, total_tunnels=0, connected_users="", if_in_bps=0, if_out_bps=0),
            },
            [
                Result(state=State.OK, summary="Users: 0, Tunnels: 0", details="Connected users: "),
            ],
        ),
        (
            "root",
            {"root": SSLVPNData(results=[Session(index=0, user_name="user01", remote_host="10.20.30.15", duration=177, subsessions=[Subsession(index=1, parent_index=0, mode="Tunnel", type="Unknown", aip="10.10.10.100", in_bytes=10, out_bytes=100, desthost="")], total_websessions=0, total_tunnels=0), Session(index=0, user_name="user02", remote_host="10.10.20.30", duration=190, subsessions=[Subsession(index=1, parent_index=0, mode="Tunnel", type="Unknown", aip="10.10.1.110", in_bytes=20, out_bytes=200, desthost="")], total_websessions=0, total_tunnels=0), Session(index=0, user_name="user03", remote_host="10.10.20.30", duration=1990, subsessions=[Subsession(index=1, parent_index=0, mode="Tunnel", type="Unknown", aip="10.10.1.111", in_bytes=1000, out_bytes=2000, desthost="")], total_websessions=0, total_tunnels=0)], vdom="root", total_users=3, total_tunnels=3, connected_users="user01, user02, user03", if_in_bps=1030, if_out_bps=2300)},
            [
                Result(state=State.OK, summary="Users: 3, Tunnels: 3", details="Connected users: user01, user02, user03"),
            ],
        ),
    ],
)

def test_check_fortios_sslvpn(item: str, section: Mapping[str, SSLVPNData], expected_check_result: Tuple) -> None:
    with patch("cmk.base.plugins.agent_based.fortios_sslvpn.get_value_store") as mock_get:
        timestamp = int((datetime.now() - timedelta(minutes=2)).timestamp())
        mock_get.return_value = {"if_in_bps": (timestamp, 0.0), "if_out_bps": (timestamp, 0.0)}
        result = list(check_fortios_sslvpn(item, section))
        for res, expected_res in zip(result, expected_check_result):
            assert res == expected_res
