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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
    register,
    render,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel, validator


class Uptime(BaseModel):
    hostname: Optional[str] = None
    utc_last_reboot: int
    snapshot_utc_time: int
    uptime: Optional[int] = 0

    # convert ms to s
    @validator("utc_last_reboot", "snapshot_utc_time", always=True)
    def convert_time(cls, v):
        return v / 1000

    @validator("uptime", always=True)
    def calculate_uptime(cls, v, values):
        if "utc_last_reboot" in values:
            utc_last_reboot = values["utc_last_reboot"]
            uptime_seconds = int(time.mktime(time.gmtime()) - time.mktime(time.gmtime(utc_last_reboot)))
            return uptime_seconds

    @property
    def summary(self):
        now = time.time()
        return f"Up since: {render.datetime(self.utc_last_reboot)} UTC, Uptime: {render.timespan(now - self.utc_last_reboot)}"


def parse_fortios_uptime(string_table) -> Uptime | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, KeyError):
        return None

    if (forti_uptime := json_data.get("results")) in ({}, []):
        return None

    return Uptime(**forti_uptime)


register.agent_section(
    name="fortios_uptime",
    parse_function=parse_fortios_uptime,
)


def discovery_fortios_uptime(section: Uptime) -> DiscoveryResult:
    yield Service()


def check_fortios_uptime(section: Uptime) -> CheckResult:
    yield Result(state=State.OK, summary=section.summary)
    yield Metric("uptime", section.uptime)


register.check_plugin(
    name="fortios_uptime",
    service_name="Uptime",
    discovery_function=discovery_fortios_uptime,
    check_function=check_fortios_uptime,
)
