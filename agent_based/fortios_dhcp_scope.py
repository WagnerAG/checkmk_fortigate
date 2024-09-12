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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
    check_levels,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.render import (
    percent,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel

DEFAULT_DHCP_LEVELS: Dict = {"dhcp_scope_levels": (80.0, 90.0)}


class IpRange(BaseModel):
    id: int
    q_origin_key: int
    start_ip: str
    end_ip: str
    vci_match: str
    vci_string: List[str]
    uci_match: str
    uci_string: List[str]
    lease_time: int


class VciString(BaseModel):
    vci_string: str
    q_origin_key: str


class ReservedAddress(BaseModel):
    id: int
    q_origin_key: int
    type: str
    ip: str
    mac: str
    action: str
    circuit_id_type: str
    circuit_id: str
    remote_id_type: str
    remote_id: str
    description: str


class DhcpServer(BaseModel):
    id: int
    q_origin_key: int
    status: str
    lease_time: int
    mac_acl_default_action: str
    forticlient_on_net_status: str
    dns_service: str
    dns_server1: str
    dns_server2: str
    dns_server3: str
    dns_server4: str
    wifi_ac_service: str
    wifi_ac1: str
    wifi_ac2: str
    wifi_ac3: str
    ntp_service: str
    ntp_server1: str
    ntp_server2: str
    ntp_server3: str
    domain: str
    wins_server1: str
    wins_server2: str
    default_gateway: str
    next_server: str
    netmask: str
    interface: str
    ip_range: List[IpRange]
    timezone_option: str
    timezone: str
    tftp_server: List[str]
    filename: str
    options: List[str]
    server_type: str
    ip_mode: str
    conflicted_ip_timeout: int
    ipsec_lease_hold: int
    auto_configuration: str
    dhcp_settings_from_fortiipam: str
    auto_managed_status: str
    ddns_update: str
    ddns_update_override: str
    ddns_server_ip: str
    ddns_zone: str
    ddns_auth: str
    ddns_keyname: str
    ddns_key: str
    ddns_ttl: int
    vci_match: str
    vci_string: List[VciString]
    exclude_range: List[str]
    reserved_address: List[ReservedAddress]

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


def parse_fortios_dhcp_scope(string_table) -> Mapping[str, DhcpServer]:
    try:
        json_data = json.loads(string_table[0][0])
        json_data = replace_hyphens(json_data)
    except (ValueError, IndexError):
        return None

    if (forti_dhcp_scope := json_data.get("results")) in ({}, []):
        return None
    
    return {str(ipaddress.IPv4Network(f"{item['default_gateway']}/{item['netmask']}", strict=False)): DhcpServer(**item) for item in forti_dhcp_scope}


register.agent_section(
    name="fortios_dhcp_scope",
    parse_function=parse_fortios_dhcp_scope,
)


def discovery_fortios_dhcp_scope(section_fortios_dhcp_scope, section_fortios_dhcp_lease) -> DiscoveryResult:
    for item in section_fortios_dhcp_scope:
        yield Service(item=item)


def check_fortios_dhcp_scope(item: str, params: Mapping[str, Any], section_fortios_dhcp_scope, section_fortios_dhcp_lease) -> CheckResult:
    dhcp_levels = params.get("dhcp_scope_levels")

    scope = section_fortios_dhcp_scope.get(item)
    
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


register.check_plugin(
    name="fortios_dhcp_scope",
    service_name="DHCP scope %s",
    sections=["fortios_dhcp_scope", "fortios_dhcp_lease"],
    discovery_function=discovery_fortios_dhcp_scope,
    check_ruleset_name="fortios_dhcp_scope",
    check_function=check_fortios_dhcp_scope,
    check_default_parameters=DEFAULT_DHCP_LEVELS,
)
