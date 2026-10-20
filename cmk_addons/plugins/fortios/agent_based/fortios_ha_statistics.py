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
from typing import List, Optional

from pydantic import BaseModel

from cmk.agent_based.v2 import AgentSection, StringTable


class VdomStats(BaseModel):
    vdom: str
    cpu_usage: float = 0
    mem_usage: float = 0
    sessions: int = 0
    sessions6: Optional[int] = 0


class HANodeStats(BaseModel):
    hostname: str
    serial_no: Optional[str] = None
    cpu_usage: float = 0
    mem_usage: float = 0
    intr_usage: Optional[float] = 0
    net_usage: Optional[float] = 0
    vir_usage: Optional[float] = 0
    sessions: int = 0
    sessions6: Optional[int] = 0
    tbyte: Optional[int] = 0
    tpacket: Optional[int] = 0
    uptime: Optional[int] = None
    per_vdom_stats: List[VdomStats] = []


class HAStatistics(BaseModel):
    nodes: List[HANodeStats]

    def node(self, hostname: str) -> Optional[HANodeStats]:
        return next((node for node in self.nodes if node.hostname == hostname), None)


def parse_fortios_ha_statistics(string_table: StringTable) -> HAStatistics | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (nodes := json_data.get("results")) in ({}, [], None):
        return None

    return HAStatistics(nodes=[HANodeStats(**node) for node in nodes])


agent_section_fortios_ha_statistics = AgentSection(
    name="fortios_ha_statistics",
    parse_function=parse_fortios_ha_statistics,
)
