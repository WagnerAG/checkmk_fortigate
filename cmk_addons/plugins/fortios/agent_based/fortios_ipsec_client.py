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

"""
Check_MK agent based checks to be used with agent_fortios Datasource

"""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    get_rate,
    get_value_store,
)
from cmk.agent_based.v2.render import networkbandwidth

from .fortios_ipsec import FortiIPSec

DISCOVERY_DEFAULT_PARAMETERS = dict({"item_enabled": False})


def discovery_fortios_ipsec_client_vpn(
    params: Mapping[str, Any],
    section: Mapping[str, FortiIPSec],
) -> DiscoveryResult:
    discover = params["item_enabled"]
    if discover:
        return

    parent_to_vpns: dict[str, list[FortiIPSec]] = {}
    for tunnel in section.values():
        if tunnel and tunnel.fct_uid and tunnel.parent:
            parent_to_vpns.setdefault(tunnel.parent, []).append(tunnel)

    for parent_name in sorted(parent_to_vpns.keys()):
        yield Service(item=f"{parent_name}")


def check_fortios_ipsec_client_vpn(
    item: str,
    params: Mapping[str, Any],
    section: Mapping[str, FortiIPSec],
) -> CheckResult:
    parent_vpns = [tunnel for tunnel in section.values() if tunnel and tunnel.fct_uid and tunnel.parent == item]

    if not parent_vpns:
        yield Result(
            state=State.OK,
            summary="Users: 0",
        )
        return

    total_users = len(parent_vpns)
    total_in_bytes = sum(tunnel.incoming_bytes or 0 for tunnel in parent_vpns)
    total_out_bytes = sum(tunnel.outgoing_bytes or 0 for tunnel in parent_vpns)

    summary = f"Users: {total_users}"

    details_lines = [f"User: {tunnel.xauth_user or 'unknown'}, Public IP: {tunnel.rgwy or 'unknown'}, Local IP: {tunnel.tun_id or 'unknown'}" for tunnel in parent_vpns]
    details = "\n".join(details_lines)

    yield Result(
        state=State.OK,
        summary=summary,
        details=details,
    )

    value_store = get_value_store()
    now = time.time()

    if total_in_bytes:
        in_rate = get_rate(
            value_store,
            "if_in_bps",
            now,
            total_in_bytes,
        )
        yield Metric("if_in_bps", in_rate)
        yield from check_levels(
            value=in_rate,
            metric_name="if_in_bps",
            label="In",
            render_func=networkbandwidth,
        )

    if total_out_bytes:
        out_rate = get_rate(
            value_store,
            "if_out_bps",
            now,
            total_out_bytes,
        )
        yield Metric("if_out_bps", out_rate)
        yield from check_levels(
            value=out_rate,
            metric_name="if_out_bps",
            label="Out",
            render_func=networkbandwidth,
        )


check_plugin_fortios_ipsec_client_vpn = CheckPlugin(
    name="fortios_ipsec_client_vpn",
    service_name="IPSec Client VPN %s",
    sections=["fortios_ipsec"],
    discovery_function=discovery_fortios_ipsec_client_vpn,
    discovery_default_parameters=DISCOVERY_DEFAULT_PARAMETERS,
    discovery_ruleset_name="fortios_ipsec_client_vpn_discovery",
    check_default_parameters={},
    check_function=check_fortios_ipsec_client_vpn,
)
