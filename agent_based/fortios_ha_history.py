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
from typing import List

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
    register,
    render,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel, validator

NUM_OUTPUT_RECORDS = 7


class Event(BaseModel):
    event: str
    time: int

    @validator("time")
    def convert_time_field(cls, v):
        return render.datetime(v)


class Section(BaseModel):
    history: List[Event]

    @property
    def summary(self):
        last_event = self.history[:1][0]
        return f"{last_event.time}: {last_event.event}"

    @property
    def details(self):
        return "\n".join(f"{last_event.time}: {last_event.event}" for last_event in self.history[:NUM_OUTPUT_RECORDS])


def parse_fortios_ha_history(string_table) -> Section | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (ha_history := json_data.get("results")) in ({}, []):
        return None

    return Section(**ha_history)


register.agent_section(
    name="fortios_ha_history",
    parse_function=parse_fortios_ha_history,
)


def discovery_fortios_ha_history(section: Section) -> DiscoveryResult:
    yield Service(item="events")


def check_fortios_ha_history(item: str, section: Section) -> CheckResult:
    yield Result(state=State.OK, summary=section.summary, details=section.details)


register.check_plugin(
    name="fortios_ha_history",
    service_name="HA history %s",
    discovery_function=discovery_fortios_ha_history,
    check_function=check_fortios_ha_history,
)
