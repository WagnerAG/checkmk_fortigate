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
from typing import List, Optional, Mapping

from pydantic import BaseModel

from cmk.agent_based.v2 import AgentSection, CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State


class HAPeer(BaseModel):
    hostname: str
    master: bool = False
    primary: bool = False
    priority: Optional[int] = None
    serial_no: Optional[str] = None
    vcluster_id: Optional[int] = None


class HACluster(BaseModel):
    peers: List[HAPeer]

    @property
    def master_peer(self) -> Optional[HAPeer]:
        for peer in self.peers:
            if peer.master:
                return peer
        for peer in self.peers:
            if peer.primary:
                return peer
        return self.peers[0] if self.peers else None

    @property
    def has_secondary(self) -> bool:
        master = self.master_peer
        if not master:
            return False
        return any(peer is not master for peer in self.peers)

    @property
    def summary(self) -> str:
        master = self.master_peer
        if not master:
            return "No master data available"

        secondary_status = "not found!" if not self.has_secondary else "see details"
        return f"Primary: {master.hostname}, Node Serial: {master.serial_no}, Priority: {master.priority}, Cluster ID: {master.vcluster_id}, Secondary nodes: {secondary_status}"

    @property
    def details(self) -> str:
        master = self.master_peer
        if not master:
            return "No data available"

        lines = [f"Primary: {master.hostname}, Node Serial: {master.serial_no}, Priority: {master.priority}, Cluster ID: {master.vcluster_id}"]
        for peer in self.peers:
            if peer is master:
                continue
            lines.append(f"Secondary: {peer.hostname}, Node Serial: {peer.serial_no}, Priority: {peer.priority}, Cluster ID: {peer.vcluster_id}")
        return "\n".join(lines)


def parse_fortios_ha_peer(string_table) -> Mapping[str, HACluster] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (ha_peers := json_data.get("results")) in ({}, []):
        return None

    peers = [HAPeer(**peer) for peer in ha_peers]
    return HACluster(peers=peers)


agent_section_fortios_ha_peer = AgentSection(
    name="fortios_ha_peer",
    parse_function=parse_fortios_ha_peer,
)


def discovery_fortios_ha_peer(section: HACluster) -> DiscoveryResult:
    if not section or not section.peers:
        return

    yield Service(item="nodes")


def check_fortios_ha_peer(item: str, section: HACluster) -> CheckResult:
    if not section:
        yield Result(
            state=State.UNKNOWN,
            summary="No HA peer data available",
        )
        return

    summary = section.summary
    details = section.details

    state = State.OK
    if not section.master_peer:
        state = State.WARN
    elif not section.has_secondary:
        state = State.WARN

    yield Result(
        state=state,
        summary=summary,
        details=details,
    )


check_plugin_fortios_ha_peer = CheckPlugin(
    name="fortios_ha_peer",
    service_name="HA cluster %s",
    discovery_function=discovery_fortios_ha_peer,
    check_function=check_fortios_ha_peer,
)
