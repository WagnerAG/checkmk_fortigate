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
from typing import (
    List,
    Optional,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import StringTable
from pydantic import BaseModel, validator


class Session(BaseModel):
    current_usage: int


class Resource(BaseModel):
    cpu: int
    memory: int
    session: Session


class ResourceResult(BaseModel):
    results: Resource
    vdom: str


class FortiResource(BaseModel):
    vdoms: Optional[List[ResourceResult]] = None
    total_cpu: Optional[int] = 0
    total_memory: Optional[int] = 0
    total_sessions: Optional[int] = 0

    @validator("total_cpu", always=True)
    def calculate_total_cpu(cls, v, values):
        total_cpu = sum(vdom.results.cpu for vdom in values.get("vdoms", []))
        return total_cpu

    @validator("total_memory", always=True)
    def calculate_total_memory(cls, v, values):
        total_memory = sum(vdom.results.memory for vdom in values.get("vdoms", []))
        return total_memory

    @validator("total_sessions", always=True)
    def calculate_total_sessions(cls, v, values):
        total_sessions = sum(vdom.results.session.current_usage for vdom in values.get("vdoms", []))
        return total_sessions


def parse_fortios_resources(string_table: StringTable) -> FortiResource | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, KeyError):
        return None

    if (forti_resources := json_data) in ({}, []):
        return None

    return FortiResource(vdoms=[ResourceResult(**item) for item in forti_resources])


register.agent_section(
    name="fortios_vdom_resources",
    parse_function=parse_fortios_resources,
)
