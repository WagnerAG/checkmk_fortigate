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
from typing import Mapping

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel


class Peer(BaseModel):
    serial_no: str
    vcluster_id: int
    priority: int
    hostname: str
    status: str

    @property
    def summary(self):
        return f"Cluster status: {self.status}, Cluster ID: {self.vcluster_id}, Priority: {self.priority}, Node Serial: {self.serial_no}"


def parse_fortios_ha_peer(string_table) -> Mapping[str, Peer] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (forti_ha_peers := json_data.get("results")) in ({}, []):
        return None

    # Add status to every node
    for peer in forti_ha_peers:
        peer["status"] = json_data["status"]

    return {item["hostname"]: Peer(**item) for item in forti_ha_peers}


register.agent_section(
    name="fortios_ha_peer",
    parse_function=parse_fortios_ha_peer,
)


def discovery_fortios_ha_peer(section: Mapping[str, Peer]) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_fortios_ha_peer(item: str, section: Mapping[str, Peer]) -> CheckResult:
    ha_peer = section.get(item)

    yield Result(state=State.OK if ha_peer.status == "success" else State.CRIT, summary=ha_peer.summary)


register.check_plugin(
    name="fortios_ha_peer",
    service_name="HA peer %s",
    discovery_function=discovery_fortios_ha_peer,
    check_function=check_fortios_ha_peer,
)
