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
from typing import Any, Dict, Mapping, Optional

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
    check_levels,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel, validator

DEFAULT_OFFSET_LEVELS: Dict = {"offset_levels": (4, 0.2, 0.5)}


class FortiNTP(BaseModel, frozen=True):
    server: str
    reachable: bool
    stratum: Optional[int] = None
    ip: Optional[str] = None
    offset: Optional[float] = 0
    selected: Optional[bool] = None

    # convert ms to s
    @validator("offset", always=True)
    def convert_offset(cls, v):
        return v / 1000

    @property
    def summary(self):
        return f"Server: {self.server}, IP: {self.ip}, Selected: {self.selected}"


def parse_fortios_ntp(string_table) -> Mapping[str, FortiNTP] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (forti_ntp_servers := json_data.get("results")) in ({}, []):
        return None

    return {item["server"]: FortiNTP(**item) for item in forti_ntp_servers}


register.agent_section(
    name="fortios_ntp",
    parse_function=parse_fortios_ntp,
)


def discovery_fortios_ntp(section: Mapping[str, FortiNTP]) -> DiscoveryResult:
    for item in section:
        ntp = section.get(item)
        if ntp.selected:
            yield Service()
            break
    for item in section:
        ntp = section.get(item)
        if ntp.reachable and ntp.offset:
            yield Service()


def check_fortios_ntp(params: Mapping[str, Any], section: Mapping[str, FortiNTP]) -> CheckResult:
    ntp = list(section.values())[0]
    if ntp:
        yield Result(state=State.OK, summary=ntp.summary)
    else:
        yield Result(state=State.UNKNOWN, summary=f"Item {ntp} not found...")
        return

    crit_stratum, warn, crit = params["offset_levels"]
    yield from check_levels(
        value=ntp.offset,
        levels_upper=(warn, crit),
        levels_lower=(-warn, -crit),
        metric_name="time_offset",
        render_func=lambda f: "%.1f ms" % (f * 1000),
        label="Time offset",
    )

    yield from check_levels(
        value=ntp.stratum,
        levels_upper=(crit_stratum, crit_stratum),
        render_func=lambda d: str(int(d)),
        label="Stratum",
    )


register.check_plugin(
    name="fortios_ntp",
    service_name="NTP Time",
    discovery_function=discovery_fortios_ntp,
    check_ruleset_name="fortios_ntp",
    check_function=check_fortios_ntp,
    check_default_parameters=DEFAULT_OFFSET_LEVELS,
)
