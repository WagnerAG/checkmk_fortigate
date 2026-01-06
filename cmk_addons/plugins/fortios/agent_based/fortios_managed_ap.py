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
import time
from typing import List, Mapping, Optional

from cmk.agent_based.v2.render import networkbandwidth
from pydantic import BaseModel

from cmk.agent_based.v2 import AgentSection, CheckPlugin, CheckResult, DiscoveryResult, GetRateError, Metric, Result, Service, State, get_rate, get_value_store, check_levels


class WiredInterface(BaseModel):
    interface: str
    bytes_rx: int
    bytes_tx: int
    packets_rx: int
    packets_tx: int
    errors_rx: int
    errors_tx: int
    dropped_rx: int
    dropped_tx: int
    collisions: int
    link_speed_mbps: int
    is_carrier_link: bool
    is_full_duplex: bool
    max_link_speed: int


class HealthMetric(BaseModel):
    value: int
    severity: str


class HealthSection(BaseModel):
    channel_utilization: Optional[HealthMetric]
    interfering_ssids: Optional[HealthMetric]
    infra_interfering_ssids: Optional[HealthMetric]
    overall: Optional[HealthMetric]


class GeneralHealth(BaseModel):
    country_code: HealthMetric
    uplink_status: List[HealthMetric]
    overall: Optional[HealthMetric]


class AccessPointHealth(BaseModel):
    general: Optional[GeneralHealth] = HealthMetric(value=99, severity="Unknown")
    overall: Optional[HealthMetric] = HealthMetric(value=99, severity="Unknown")


class Radio(BaseModel):
    radio_id: int
    mode: str
    client_count: Optional[int] = 0
    health: Optional[AccessPointHealth] | None = None


class SSIDRadio(BaseModel):
    radio: int
    list: List[str]


class LLDP(BaseModel):
    local_port: str
    chassis_id: str
    system_name: str
    system_description: str
    capability: str
    port_id: str
    port_description: str
    mau_operating_mode: str
    ip: str
    vlan: int


class AccessPoint(BaseModel):
    name: str
    serial: str
    status: str
    state: str
    clients: int
    local_ipv4_addr: Optional[str] = "Unknown"
    board_mac: str
    last_reboot_time: Optional[str] = "Unknown"
    ssid: List[SSIDRadio]
    lldp: Optional[List[LLDP]] = None
    lldp_enable: bool
    os_version: Optional[str] = "Unknown"
    radio: List[Radio]
    eos: Optional[bool] = False
    wired: List[WiredInterface]
    health: AccessPointHealth | None = None
    cpu_usage: int
    mem_free: int
    mem_total: int

    @property
    def summary_status(self):
        return f"Status: {self.status}, State: {self.state}, Clients: {self.clients}, IP: {self.local_ipv4_addr}"

    @property
    def details(self):
        ssid_result = ""
        for item in self.ssid:
            radio = f"- Radio {item.radio}:"
            ssids = ""
            for ssid in item.list:
                ssids += f"{ssid}  "
            ssid_result += f"{radio} {str(ssids)}\n"

        radio_health = ""
        for item in self.radio:
            if item.mode == "AP":
                radio_health += f"- Radio {item.radio_id}: {item.health.overall.severity}\n"

        if self.lldp_enable and len(self.lldp) > 0:
            lldp_result = ""
            for item in self.lldp:
                lldp_result += f"""- Local port: {item.local_port}
                - Remote device: {item.system_name}
                - Remote description: {item.system_description}
                - Remote port: {item.port_id}\n
                """
        else:
            lldp_result = "No LLDP data available. LLDP enabled on both sides?"

        return f"""
            Serial: {self.serial}
            AP MAC: {self.board_mac}
            Last reboot: {self.last_reboot_time}
            
            Health:
            - AP general: {self.health.general.overall.severity}
            {radio_health}
            SSIDs:\n{ssid_result}
            LLDP information:
            {lldp_result}
            """


def parse_fortios_managed_ap(string_table) -> Mapping[str, AccessPoint] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None
    if (forti_aps := json_data.get("results")) in ({}, []):
        return None
    return {item["name"]: AccessPoint(**item) for item in forti_aps}


agent_section_fortios_managed_ap = AgentSection(
    name="fortios_managed_ap",
    parse_function=parse_fortios_managed_ap,
)


def discovery_fortios_managed_ap(section: Mapping[str, AccessPoint]) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_fortios_managed_ap(item: str, section: Mapping[str, AccessPoint]) -> CheckResult:
    ap = section.get(item)
    if not ap:
        yield Result(state=State.UNKNOWN, summary=f"AP {item} is missing")
        return
    if ap.status == "disconnected":
        yield Result(state=State.CRIT, summary=f"{ap.summary_status}", details=ap.details)
    else:
        yield Result(state=State.OK if ap.state == "authorized" else State.WARN, summary=f"{ap.summary_status}", details=ap.details)

    value_store = get_value_store()

    for interface in ap.wired:
        if interface.link_speed_mbps:
            for key in ["bytes_tx", "bytes_rx", "errors_tx", "errors_rx", "dropped_tx", "dropped_rx", "collisions"]:
                attribute = getattr(interface, key)
                value = 0
                try:
                    time_now = time.time()
                    value = get_rate(value_store, key, time_now, attribute, raise_overflow=False)
                except GetRateError:
                    pass

                if key == "bytes_rx":
                    yield from check_levels(
                        value=value,
                        label="In",
                        render_func=networkbandwidth,
                    )
                    yield Metric(name="if_in_bps", value=value * 8, boundaries=(0, None))

                elif key == "bytes_tx":
                    yield from check_levels(
                        value=value,
                        label="Out",
                        render_func=networkbandwidth,
                    )
                    yield Metric(name="if_out_bps", value=value * 8, boundaries=(0, None))
                else:
                    yield Metric(name=f"{interface.interface}_{key}", value=value, boundaries=(0, None))

    try:
        memory_usage = ((ap.mem_total - ap.mem_free) / ap.mem_total) * 100
    except ZeroDivisionError:
        memory_usage = 0

    yield Metric("memory_util", value=memory_usage, boundaries=(0, 100))

    yield Metric("util", ap.cpu_usage, boundaries=(0, 100))

    yield Metric(name="clients", value=ap.clients, boundaries=(0, None))


check_plugin_fortios_managed_ap = CheckPlugin(
    name="fortios_managed_ap",
    service_name="AP %s",
    discovery_function=discovery_fortios_managed_ap,
    check_function=check_fortios_managed_ap,
)
