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

import ipaddress
import json
from typing import Any, Dict, List, Mapping

from cmk.agent_based.v2.render import percent
from pydantic import BaseModel

from cmk.agent_based.v2 import AgentSection, CheckPlugin, CheckResult, DiscoveryResult, Metric, Result, Service, State, check_levels

DEFAULT_DHCP_LEVELS: Dict = {"dhcp_scope_levels": ("fixed", (80, 90))}


class IpRange(BaseModel):
    start_ip: str
    end_ip: str


class DhcpServer(BaseModel):
    q_origin_key: Any
    status: str
    interface: str
    ip_range: List[IpRange]

    @property
    def summary(self) -> str:
        return f"Status: {self.status}, Interface: {self.interface}"


def replace_hyphens(d):
    if isinstance(d, dict):
        return {k.replace("-", "_"): replace_hyphens(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [replace_hyphens(item) for item in d]
    else:
        return d


def parse_fortios_dhcp_scope(string_table) -> Mapping[str, DhcpServer] | None:
    try:
        json_data = json.loads(string_table[0][0])
        json_data = replace_hyphens(json_data)
    except (ValueError, IndexError):
        return None

    forti_dhcp_scope = json_data.get("results")
    if not forti_dhcp_scope:
        return None

    return {str(ipaddress.IPv4Network(f"{item['default_gateway']}/{item['netmask']}", strict=False)): DhcpServer(**item) for item in forti_dhcp_scope}


agent_section_fortios_dhcp_scope = AgentSection(
    name="fortios_dhcp_scope",
    parse_function=parse_fortios_dhcp_scope,
)


def discovery_fortios_dhcp_scope(section_fortios_dhcp_scope, section_fortios_dhcp_lease) -> DiscoveryResult:
    if not section_fortios_dhcp_scope:
        return
    for item in section_fortios_dhcp_scope:
        yield Service(item=item)


def check_fortios_dhcp_scope(item: str, params: Mapping[str, Any], section_fortios_dhcp_scope, section_fortios_dhcp_lease) -> CheckResult:
    dhcp_levels = params.get("dhcp_scope_levels")

    scope = section_fortios_dhcp_scope.get(item)

    if not scope:
        return

    total_ip_count = []
    for ip_range in scope.ip_range:
        total_ip_count.append(int(ipaddress.IPv4Address(ip_range.end_ip)) - int(ipaddress.IPv4Address(ip_range.start_ip)) + 1)
    total_ip_count = sum(total_ip_count)

    used_ip_count = 0
    conflicted_details = []
    if section_fortios_dhcp_lease:
        for lease in section_fortios_dhcp_lease:
            lease_data = section_fortios_dhcp_lease.get(lease)
            if scope.q_origin_key == lease_data.server_mkey:
                used_ip_count += 1
                if lease_data.status == "conflicted":
                    conflicted_details.append(str(f"MAC: {lease_data.mac}, IP: {lease_data.ip}"))

    if conflicted_details:
        details = "Conflicted leases:\n"
        for conflict in conflicted_details:
            details += str(f"{conflict}\n")

    scope_usage = 100 / total_ip_count * used_ip_count

    yield Metric("scope_usage", used_ip_count, boundaries=(0, total_ip_count))
    yield from check_levels(
        value=scope_usage,
        label="Scope usage",
        render_func=percent,
        boundaries=(0, total_ip_count),
        levels_upper=dhcp_levels,
    )
    if len(conflicted_details) > 0:
        yield Result(state=State.WARN, summary=f"{scope.summary}, IP conflicts: {len(conflicted_details)}, Total IPs: {total_ip_count}, Leased IPs: {used_ip_count}, Available IPs: {total_ip_count - used_ip_count}", details=details)
    else:
        yield Result(state=State.OK, summary=f"{scope.summary}, Total IPs: {total_ip_count}, Leased IPs: {used_ip_count}, Available IPs: {total_ip_count - used_ip_count}")


check_plugin_fortios_dhcp_scope = CheckPlugin(
    name="fortios_dhcp_scope",
    service_name="DHCP scope %s",
    sections=["fortios_dhcp_scope", "fortios_dhcp_lease"],
    discovery_function=discovery_fortios_dhcp_scope,
    check_ruleset_name="fortios_dhcp_scope",
    check_function=check_fortios_dhcp_scope,
    check_default_parameters=DEFAULT_DHCP_LEVELS,
)
