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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    GetRateError,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    get_rate,
    get_value_store,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.render import networkbandwidth
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel, Field, validator


class Subsession(BaseModel):
    index: int
    parent_index: int
    mode: str
    type: str
    aip: str
    in_bytes: int
    out_bytes: int
    desthost: str


class Session(BaseModel):
    index: Optional[int] = 0
    user_name: Optional[str] = None
    remote_host: Optional[str] = None
    duration: Optional[int] = None
    subsessions: Optional[List[Subsession]] = None
    total_websessions: int = 0
    total_tunnels: int = 0


class SSLVPNData(BaseModel):
    results: List[Session]
    vdom: str

    total_users: int = Field(0, alias="total_users")
    total_tunnels: int = Field(0, alias="total_users")
    connected_users: str = Field("", alias="connected_users")
    if_in_bps: int = Field(0, alias="if_in_bps")
    if_out_bps: int = Field(0, alias="if_out_bps")

    @validator("total_users", always=True)
    def get_total_users(cls, v, values):
        return len(values.get("results", []))

    @validator("connected_users", always=True)
    def get_connected_user_names(cls, v, values):
        user_names = [result.user_name for result in values.get("results", [])]
        return ", ".join(user_names)

    @validator("total_tunnels", always=True)
    def calculate_tunnels(cls, v, values):
        total_subsessions = sum(len(result.subsessions) for result in values.get("results", []))
        return total_subsessions

    @validator("if_in_bps", always=True)
    def calculate_total_in_bps(cls, v, values):
        total_in = sum(subsession.in_bytes for result in values.get("results", []) for subsession in result.subsessions)
        return total_in

    @validator("if_out_bps", always=True)
    def calculate_total_out_bps(cls, v, values):
        total_out = sum(subsession.out_bytes for result in values.get("results", []) for subsession in result.subsessions)
        return total_out

    @property
    def summary(self):
        return f"Users: {self.total_users}, Tunnels: {self.total_tunnels}"

    @property
    def details(self):
        return f"Connected users: {self.connected_users}"


def parse_fortios_sslvpn(string_table) -> dict[str, SSLVPNData] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    return {item["vdom"]: SSLVPNData(**item) for item in json_data}


register.agent_section(
    name="fortios_sslvpn",
    parse_function=parse_fortios_sslvpn,
)


def discovery_fortios_sslvpn(section: SSLVPNData) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_fortios_sslvpn(item: str, section: Mapping[str, SSLVPNData]) -> CheckResult:
    vdom_sslvpn=section.get(item)
    
    if not vdom_sslvpn:
        yield Result(state=State.UNKNOWN, summary=f"SSLVPN data for VDOM {item} is missing")
    
    if vdom_sslvpn == 0:
        summary = "Enabled, Users: 0, Tunnels: 0"
    else:
        summary = vdom_sslvpn.summary

    yield Result(state=State.OK, summary=summary, details=vdom_sslvpn.details)

    value_store = get_value_store()
    now_time = time.time()

    in_bytes = 0
    try:
        in_bytes = get_rate(value_store, "if_in_bps", now_time, vdom_sslvpn.if_in_bps, raise_overflow=False)
    except GetRateError:
        pass

    yield Metric(name="if_in_bps", value=in_bytes, boundaries=(0, None))
    yield from check_levels(
        value=in_bytes,
        label="In",
        render_func=networkbandwidth,
    )

    out_bytes = 0
    try:
        out_bytes = get_rate(value_store, "if_out_bps", now_time, vdom_sslvpn.if_out_bps, raise_overflow=False)
    except GetRateError:
        pass

    yield Metric(name="if_out_bps", value=out_bytes, boundaries=(0, None))
    yield from check_levels(
        value=out_bytes,
        label="Out",
        render_func=networkbandwidth,
    )


register.check_plugin(
    name="fortios_sslvpn",
    service_name="SSLVPN VDOM %s",
    discovery_function=discovery_fortios_sslvpn,
    check_function=check_fortios_sslvpn,
)
