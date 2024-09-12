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

import json
import re
import time
from enum import IntEnum
from typing import Any, Mapping, Optional, Union

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    GetRateError,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    get_rate,
    get_value_store,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.render import (
    networkbandwidth,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel


class IgmpSnoopingGroup(BaseModel):
    group_count: int


class Transceiver(BaseModel):
    vendor: str
    vendor_part_number: str


class InterfaceData(BaseModel):
    group_count: int


class PhysicalPort(BaseModel):
    access_mode: str
    admin_vlan: Optional[str]
    aggregator_mode: str
    allowed_vlans_all: str
    arp_inspection_trust: str
    bundle: str
    description: str
    discard_mode: str
    edge_port: str
    export_to: str
    export_to_pool: str
    export_to_pool_flag: int
    fec_capable: int
    fec_state: str
    fgt_peer_device_name: str
    fgt_peer_port_name: str
    fiber_port: int
    flags: int
    flow_control: str
    fortilink_port: int
    ip_source_guard: str
    isl_local_trunk_name: str
    isl_peer_device_name: str
    isl_peer_port_name: str
    lacp_speed: str
    learning_limit: int
    lldp_profile: str
    lldp_status: str
    loop_guard: str
    loop_guard_timeout: int
    mac_addr: str # Used
    matched_dpp_intf_tags: str
    matched_dpp_policy: str
    max_bundle: int
    mclag_icl_port: int
    media_type: str
    member_withdrawal_behavior: str
    min_bundle: int
    mode: str
    p2p_port: int
    packet_sample_rate: int
    packet_sampler: str
    pause_meter: int
    pause_meter_resume: str
    poe_capable: Optional[int]
    poe_max_power: str
    poe_pre_standard_detection: str
    poe_standard: str
    poe_status: Optional[str]
    poe_: Optional[str]
    port_name: str
    port_number: int
    port_owner: str
    port_policy: str
    port_prefix_type: int
    port_security_policy: str
    port_selection_criteria: str
    ptp_policy: str
    q_origin_key: str
    qos_policy: str
    rpvst_port: str
    sample_direction: str
    sflow_counter_interval: int
    speed: Optional[Union[str, int]]
    speed_mask: int
    stacking_port: int
    status: Optional[str]
    sticky_mac: str
    storm_control_policy: str
    stp_bpdu_guard: str
    stp_bpdu_guard_timeout: int
    stp_root_guard: str
    stp_state: str
    switch_id: str
    trunk_member: int
    type: str
    virtual_port: int
    vlan: Optional[str]
    collisions: int
    crc_alignments: int
    fragments: int
    jabbers: int
    l3packets: int
    rx_bcast: int
    rx_bytes: int
    rx_drops: int
    rx_errors: int
    rx_mcast: int
    rx_oversize: int
    rx_packets: int
    rx_ucast: int
    tx_bcast: int
    tx_bytes: int
    tx_drops: int
    tx_errors: int
    tx_mcast: int
    tx_oversize: int
    tx_packets: int
    tx_ucast: int
    undersize: int
    duplex: Optional[str] = None
    port_status: Optional[str] = None
    igmp_snooping_group: Optional[IgmpSnoopingGroup] = None
    interface: Optional[str] = None
    isl_peer_trunk_name: Optional[str] = None
    mclag_icl: Optional[bool] = None
    port_power: Optional[float] = 0.0
    power_status: Optional[int] = 0
    stp_status: Optional[str] = None
    transceiver: Optional[Transceiver] = None

    @property
    def summary(self):
        port_power = str(f"{self.port_power:.2f} W")
        return f"[{self.description if self.description != '' else ''}], ({self.port_status}), MAC: {self.mac_addr}, Media Type: {self.media_type}, Speed: {self.speed}, Duplex: {self.duplex}, PoE Power: {port_power if Power(self.power_status) == 2 else Power(self.power_status)}"


class Power(IntEnum):
    Disabled = 0
    Searching = 1
    Delivering = 2
    TestMode = 3
    Fault = 4
    OtherFault = 5
    RequiresPower = 6

    def __str__(self):
        return self.name


DISCOVERY_DEFAULT_PARAMETERS = dict({"fortios_switch_interface_discovered": []})


def replace_hyphens(d):
    if isinstance(d, dict):
        return {k.replace("-", "_"): replace_hyphens(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [replace_hyphens(item) for item in d]
    else:
        return d


def parse_fortios_switch_interface(string_table) -> Mapping[str, PhysicalPort] | None:
    try:
        json_data = json.loads(string_table[0][0])

        if (port_stats := json_data.get("switch_port_stats")) is not None:
            all_port_stats = replace_hyphens(port_stats.get("ports"))

        if (port_details := json_data.get("switch_status")) is not None:
            all_port_status = replace_hyphens(port_details.get("ports"))

        if (ports := json_data.get("switch_ports")) is not None:
            all_ports = replace_hyphens(ports.get("ports"))

        for status in all_port_status:
            port_name = status.get("port_name")
            for port, stats in all_port_stats.items():
                if port == port_name:
                    for attribute in stats:
                        status[attribute] = stats[attribute]

            for data in all_ports:
                if port_name == (data.get("interface")):
                    for attr in data:
                        if attr not in ["vlan", "poe_capable", "poe_status"]:
                            if attr == "status":
                                status["port_status"] = data.get(attr)
                            else:
                                status[attr] = data.get(attr)

    except (ValueError, IndexError):
        return None
    
    return {item["port_name"]: PhysicalPort(**item) for item in all_port_status}


def discovery_fortios_switch_interface(params: Mapping[str, Any], section: Mapping[str, PhysicalPort]) -> DiscoveryResult:
    for item in section:
        interface = section.get(item)

        if interface.port_status == "up":
            if params["fortios_switch_interface_discovered"]:
                if any(re.search(pattern, interface.description) for pattern in params["fortios_switch_interface_discovered"]):
                    yield Service(item=item)
            else:
                yield Service(item=item)


def check_fortios_switch_interface(item: str, section: Mapping[str, PhysicalPort]) -> CheckResult:
    interface = section.get(item)
    if not interface:
        yield Result(state=State.UNKNOWN, summary=f"Interface {item} is missing")
        return

    yield Result(state=State.OK, summary=interface.summary)

    value_store = get_value_store()
    time_now = time.time()

    for key in ["rx_bytes", "tx_bytes", "tx_mcast", "tx_bcast", "rx_mcast", "rx_bcast", "rx_errors", "tx_errors", "tx_drops", "rx_drops", "collisions", "crc_alignments"]:
        if hasattr(interface, key):
            attribute = getattr(interface, key)
            value = 0
            try:
                value = get_rate(value_store, f"{key}", time_now, attribute, raise_overflow=False)
            except GetRateError:
                pass

            if key == "rx_bytes":
                yield from check_levels(
                    value=value / 8,
                    label="In",
                    render_func=networkbandwidth,
                )
                yield Metric(name="if_in_bps", value=value, boundaries=(0, None))

            elif key == "tx_bytes":
                yield from check_levels(
                    value=value / 8,
                    label="Out",
                    render_func=networkbandwidth,
                )
                yield Metric(name="if_out_bps", value=value, boundaries=(0, None))
            else:
                yield Metric(name=f"{key}", value=value, boundaries=(0, None))


register.agent_section(
    name="fortios_managed_switch_interface",
    parse_function=parse_fortios_switch_interface,
)


register.check_plugin(
    name="fortios_managed_switch_interface",
    service_name="Interface %s",
    discovery_function=discovery_fortios_switch_interface,
    sections=["fortios_managed_switch_interface"],
    discovery_default_parameters=DISCOVERY_DEFAULT_PARAMETERS,
    discovery_ruleset_name="discovery_fortios_switch_interface",
    check_function=check_fortios_switch_interface,
)
