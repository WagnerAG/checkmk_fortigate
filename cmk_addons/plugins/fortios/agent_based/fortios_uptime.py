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
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from cmk.agent_based.v2.render import datetime, timespan
from cmk.agent_based.v2 import AgentSection, CheckPlugin, CheckResult, DiscoveryResult, Metric, Result, Service, State


class Uptime(BaseModel):
    hostname: Optional[str] = None
    utc_last_reboot: int
    snapshot_utc_time: int
    uptime: Optional[int] = 0

    # convert ms to s
    @field_validator("utc_last_reboot", "snapshot_utc_time", mode="before")
    @classmethod
    def convert_time(cls, v):
        return v / 1000 if v is not None else None

    @model_validator(mode="after")
    def calculate_uptime(self):
        if self.utc_last_reboot is not None:
            now = time.time()
            reboot = self.utc_last_reboot
            self.uptime = int(now - reboot)
        return self

    @property
    def summary(self):
        now = time.time()
        return f"Up since: {datetime(self.utc_last_reboot)} UTC, Uptime: {timespan(now - self.utc_last_reboot)}"


def parse_fortios_uptime(string_table) -> Uptime | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, KeyError):
        return None

    if (forti_uptime := json_data.get("results")) in ({}, []):
        return None

    return Uptime(**forti_uptime)


agent_section_fortios_uptime = AgentSection(
    name="fortios_uptime",
    parse_function=parse_fortios_uptime,
)


def discovery_fortios_uptime(section: Uptime) -> DiscoveryResult:
    yield Service()


def check_fortios_uptime(section: Uptime) -> CheckResult:
    yield Result(state=State.OK, summary=section.summary)
    yield Metric("uptime", section.uptime)


check_plugin_fortios_uptime = CheckPlugin(
    name="fortios_uptime",
    service_name="Uptime",
    discovery_function=discovery_fortios_uptime,
    check_function=check_fortios_uptime,
)
