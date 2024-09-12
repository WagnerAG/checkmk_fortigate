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


class Switch(BaseModel, frozen=True):
    status: str
    name: str
    serial: str
    state: str
    fgt_peer_intf_name: str
    connecting_from: str
    join_time: str
    type: str
    is_l3: str
    max_poe_budget: int
    igmp_snooping_supported: bool
    dhcp_snooping_supported: bool
    mc_lag_supported: bool
    led_blink_supported: bool
    os_version: str

    @property
    def summary(self) -> str:
        return f"Switch status: {self.status}, Connection state: {self.state}, Connection from: {self.connecting_from}"
    
    @property
    def details(self) -> str:
        return f"Serial: {self.serial}\n, Interface: {self.fgt_peer_intf_name}\n, Join Time: {self.join_time}\n, Type: {self.type}\n, IS Layer3: {self.is_l3}\n, POE Budget: {self.max_poe_budget}"


def parse_fortios_managed_switch(string_table) -> Mapping[str, Switch] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (forti_switches := json_data.get("results")) in ({}, []):
        return None

    return {item["name"]: Switch(**item) for item in forti_switches}


register.agent_section(
    name="fortios_managed_switch",
    parse_function=parse_fortios_managed_switch,
)


def discovery_fortios_managed_switch(section: Mapping[str, Switch]) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_fortios_managed_switch(item: str, section: Switch) -> CheckResult:
    switch = section.get(item)
    if switch.status == "Connected":
        yield Result(state=State.OK, summary=switch.summary, details=switch.details)
    else:
        yield Result(state=State.ERROR, summary=switch.summary, details=switch.defails)


register.check_plugin(
    name="fortios_managed_switch",
    service_name="Switch %s",
    discovery_function=discovery_fortios_managed_switch,
    check_function=check_fortios_managed_switch,
)
