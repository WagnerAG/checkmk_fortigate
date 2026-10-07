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

import json
from typing import List, Optional

from cmk.agent_based.v2 import AgentSection, StringTable
from pydantic import BaseModel, model_validator


class UsageSample(BaseModel):
    current: int


class ResourceUsage(BaseModel):
    cpu: List[UsageSample]
    mem: List[UsageSample]
    session: List[UsageSample]


class FortiResource(BaseModel):
    results: ResourceUsage
    total_cpu: Optional[int] = 0
    total_memory: Optional[int] = 0
    total_sessions: Optional[int] = 0

    @model_validator(mode="after")
    def calculate_totals(self):
        self.total_cpu = self.results.cpu[0].current
        self.total_memory = self.results.mem[0].current
        self.total_sessions = self.results.session[0].current
        return self


def parse_fortios_resources(string_table: StringTable) -> FortiResource | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, KeyError):
        return None

    if not json_data:
        return None

    return FortiResource(**json_data)


agent_section_fortios_vdom_resources = AgentSection(
    name="fortios_vdom_resources",
    parse_function=parse_fortios_resources,
)
