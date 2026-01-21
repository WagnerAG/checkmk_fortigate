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
from typing import Dict
from unittest.mock import patch

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_ipsec import FortiIPSec
from cmk_addons.plugins.fortios.agent_based.fortios_ipsec_client import (
    discovery_fortios_ipsec_client_vpn,
    check_fortios_ipsec_client_vpn,
)


def _create_minimal_fortios_ipsec(
    name: str,
    fct_uid: str | None = None,
    parent: str | None = None,
    xauth_user: str | None = None,
    rgwy: str | None = None,
    tun_id: str | None = None,
    tunnels_total: int = 0,
    tunnels_up: int = 0,
    tunnels_down: int = 0,
    incoming_bytes: int = 0,
    outgoing_bytes: int = 0,
) -> FortiIPSec:
    return FortiIPSec(
        name=name,
        proxyid=[],
        fct_uid=fct_uid,
        parent=parent,
        xauth_user=xauth_user,
        rgwy=rgwy,
        tun_id=tun_id,
        tunnels_total=tunnels_total,
        tunnels_up=tunnels_up,
        tunnels_down=tunnels_down,
        incoming_bytes=incoming_bytes,
        outgoing_bytes=outgoing_bytes,
        type="",
        connection_count=0,
        creation_time=0,
    )


IPSEC_CLIENT_SECTION: Dict[str, FortiIPSec] = {
    "client_user1": _create_minimal_fortios_ipsec(
        name="client_user1",
        fct_uid="fct123",
        parent="FGT-ClientVPN",
        xauth_user="user01",
        rgwy="1.2.3.4",
        tun_id="10.20.30.10",
        tunnels_total=2,
        tunnels_up=2,
        tunnels_down=0,
        incoming_bytes=1000000,
        outgoing_bytes=500000,
    ),
    "client_user2": _create_minimal_fortios_ipsec(
        name="client_user2",
        fct_uid="fct456",
        parent="FGT-ClientVPN",
        xauth_user="user02",
        rgwy="5.6.7.8",
        tun_id="10.20.30.11",
        tunnels_total=1,
        tunnels_up=0,
        tunnels_down=1,
        incoming_bytes=200000,
        outgoing_bytes=300000,
    ),
    "other_tunnel": _create_minimal_fortios_ipsec(
        name="other_tunnel",
        fct_uid=None,
        parent=None,
        xauth_user=None,
        rgwy=None,
        tun_id=None,
    ),
}

DISCOVERY_PARAMS_ENABLED = {"item_enabled": False}
DISCOVERY_PARAMS_DISABLED = {"item_enabled": True}


@pytest.mark.parametrize(
    "params, section, expected_services",
    [
        (
            DISCOVERY_PARAMS_ENABLED,
            IPSEC_CLIENT_SECTION,
            [
                Service(item="FGT-ClientVPN"),
            ],
        ),
        (
            DISCOVERY_PARAMS_DISABLED,
            IPSEC_CLIENT_SECTION,
            [],  # No services when disabled
        ),
    ],
)
def test_discovery_fortios_ipsec_client_vpn(
    params: dict,
    section: Dict[str, FortiIPSec],
    expected_services: list[Service],
) -> None:
    assert list(discovery_fortios_ipsec_client_vpn(params, section)) == expected_services


@pytest.mark.parametrize(
    "item, section, expected_results",
    [
        (
            "FGT-ClientVPN",
            IPSEC_CLIENT_SECTION,
            [
                Result(
                    state=State.OK,
                    summary="Users: 2",
                    details="User: user01, Public IP: 1.2.3.4, Local IP: 10.20.30.10\nUser: user02, Public IP: 5.6.7.8, Local IP: 10.20.30.11",
                ),
            ],
        ),
        (
            "nonexistent_parent",
            IPSEC_CLIENT_SECTION,
            [
                Result(
                    state=State.OK,
                    summary="Users: 0",
                ),
            ],
        ),
        (
            "FGT-ClientVPN",
            {
                "empty": _create_minimal_fortios_ipsec(
                    name="empty",
                    fct_uid=None,
                    parent=None,
                )
            },
            [
                Result(
                    state=State.OK,
                    summary="Users: 0",
                ),
            ],
        ),
    ],
)
def test_check_fortios_ipsec_client_vpn(
    item: str,
    section: Dict[str, FortiIPSec],
    expected_results: list[Result],
) -> None:
    with patch("cmk_addons.plugins.fortios.agent_based.fortios_ipsec_client.get_value_store") as mock_vs:
        timestamp = int((datetime.now() - timedelta(minutes=2)).timestamp())
        mock_vs.return_value = {
            "if_in_bps": (timestamp, 0.0),
            "if_out_bps": (timestamp, 0.0),
        }

        results = list(check_fortios_ipsec_client_vpn(item, {}, section))

        for result, expected in zip(results[:2], expected_results, strict=False):
            assert result == expected
