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
from typing import Tuple
from unittest.mock import patch

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_interface import (
    Interface,
    check_fortios_interfaces,
    parse_fortios_interfaces,
)
from cmk.base.plugins.agent_based.fortios_interface_cmdb import InterfaceCMDB


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [['[{"http_method":"GET","revision":"1697974233.46042","results":{"aggData01.3001":{"id":"aggData01.3001","name":"aggData01.3001","alias":"","mac":"00:00:00:00:00:00","ip":"10.10.30.30","mask":29,"link":true,"speed":6250000000.0,"duplex":1,"tx_packets":1827,"rx_packets":8921050,"tx_bytes":89580,"rx_bytes":825968722,"tx_errors":0,"rx_errors":0,"vlanid":3001,"interface":"aggData01"}},"vdom":"VDOM00","path":"system","name":"interface","action":"","status":"success","serial":"Serial01","version":"v7.0.12","build":6681}]']],
            {"aggData01.3001": Interface(id="aggData01.3001", name="aggData01.3001", alias="", mac="00:00:00:00:00:00", ip="10.10.30.30", mask=29, link=True, speed=6250000000.0, duplex=1, tx_packets=1827, rx_packets=8921050, tx_bytes=89580, if_out_bps=716640, rx_bytes=825968722, if_in_bps=6607749776, tx_errors=0, rx_errors=0, vlanid=3001, interface="aggData01", vdom="VDOM00")},
        ),
    ],
)
def test_parse_fortios_interfaces(string_table, expected_section) -> None:
    assert parse_fortios_interfaces(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section_fortios_interfaces, section_fortios_interfaces_cmdb, expected_check_result",
    [
        (
            "aggData01.3001",
            {
                "aggData01.3001": Interface(id="aggData01.3001", name="aggData01.3001", alias="", mac="00:00:00:00:00:00", ip="10.10.30.30", mask=29, link=True, speed=6250000000.0, duplex=1, tx_packets=1827, rx_packets=8921050, tx_bytes=89580, if_out_bps=716640, rx_bytes=825968722, if_in_bps=6607749776, tx_errors=0, rx_errors=0, vlanid=3001, interface="aggData01", description="Agg", interface_type="Vlan", vdom="VDOM00"),
            },
            {
                "Interface 1": InterfaceCMDB(
                    algorithm="L4",
                    alias="Interface 1",
                    allowaccess="ping",
                    arpforward="enable",
                    bfd="global",
                    defaultgw="enable",
                    description="",
                    detectprotocol="ping",
                    detectserver="",
                    devindex=42,
                    distance=5,
                    external="disable",
                    gwdetect="disable",
                    inbandwidth=0,
                    interface="LAN",
                    internal=0,
                    ip="10.10.10.10 255.255.255.0",
                    ipmac="disable",
                    ipunnumbered="0.0.0.0",
                    macaddr="00:00:00:00:00:00",
                    mode="static",
                    mtu=1500,
                    name="Interface 1",
                    ndiscforward="enable",
                    outbandwidth=0,
                    password="",
                    priority=1,
                    q_origin_key="Interface 1",
                    role="undefined",
                    speed="auto",
                    status="up",
                    stp="disable",
                    stpforward="disable",
                    subst="disable",
                    tagging=[],
                    trunk="disable",
                    type="vlan",
                    username="",
                    vdom="root",
                    vindex=0,
                    vlanforward="disable",
                    vlanid=90,
                    vrf=0,
                    wccp="disable",
                    weight=0,
                ),
            },
            [
                Metric(name="rx_packets", value=0.0, boundaries=(0, None)),
                Metric(name="tx_packets", value=0.0, boundaries=(0, None)),
                Metric(name="if_in_bps", value=0.0, boundaries=(0, None)),
                Result(state=State.OK, summary="In: 0.00 Bit/s"),
                Metric(name="if_out_bps", value=0.0, boundaries=(0, None)),
                Result(state=State.OK, summary="Out: 0.00 Bit/s"),
                Metric(name="rx_errors", value=0, boundaries=(0, None)),
                Metric(name="tx_errors", value=0, boundaries=(0, None)),
            ],
        ),
    ],
)
def test_check_fortios_interfaces(item: str, section_fortios_interfaces, section_fortios_interfaces_cmdb, expected_check_result: Tuple) -> None:
    with patch("cmk.base.plugins.agent_based.fortios_interface.get_value_store") as mock_get:
        timestamp = int((datetime.now() - timedelta(minutes=2)).timestamp())
        mock_get.return_value = {"rx_packets": (timestamp, 0.0), "tx_packets": (timestamp, 0.0)}
        mock_get.return_value = {"if_in_bps": (timestamp, 0.0), "if_out_bps": (timestamp, 0.0)}
        mock_get.return_value = {"rx_errors": (timestamp, 0.0), "tx_errors": (timestamp, 0.0)}
        result = list(check_fortios_interfaces(item, section_fortios_interfaces, section_fortios_interfaces_cmdb))
        for res, expected_res in zip(result, expected_check_result):
            assert res == expected_res
