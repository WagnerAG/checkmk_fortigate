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
import re
import time
from enum import IntEnum
from typing import Any, Dict, List, Mapping, Optional

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
from cmk.base.plugins.agent_based.agent_based_api.v1.render import (
    networkbandwidth,
    nicspeed,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult
from pydantic import BaseModel, RootModel, field_validator, model_validator


class Interface(BaseModel):
    id: Optional[str] = None
    name: str
    alias: Optional[str] = None
    mac: Optional[str] = None
    ip: Optional[str] = None
    mask: Optional[int] = None
    link: bool
    speed: Optional[float] = None
    duplex: Optional[int] = None
    tx_packets: int
    rx_packets: int
    tx_bytes: int
    if_out_bps: Optional[int] = 0
    if_out_errors: Optional[int] = 0
    rx_bytes: int
    if_in_bps: Optional[int] = 0
    if_in_errors: Optional[int] = 0
    tx_errors: int
    rx_errors: int
    vlanid: Optional[int] = None
    interface: Optional[str] = None
    vdom: Optional[str] = None
    description: Optional[str] = None
    interface_type: Optional[str] = None

    # convert bytes to bps
    @model_validator(mode="after")
    @classmethod
    def calculate_derived_fields(cls, model):
        if model.tx_bytes is not None:
            model.if_out_bps = model.tx_bytes * 8
        return model

    @model_validator(mode="after")
    @classmethod
    def calculate_if_in_bps(cls, model):
        if model.rx_bytes is not None:
            model.if_in_bps = model.rx_bytes * 8
        return model

    @field_validator("if_in_errors", mode="before")
    @classmethod
    def map_if_in_errors(cls, value):
        return value

    @field_validator("if_out_errors", mode="before")
    @classmethod
    def map_if_in_discards(cls, value):
        return value

    # convert speed from (bps) to (Bps)
    @field_validator("speed", mode="before")
    @classmethod
    def calculate_speed(cls, value):
        return value * 125000

    @property
    def summary(self):
        description = (f"{self.alias if self.alias != '' else self.description if self.description else ''}").replace("(", "[").replace(")", "]")
        return f"{description} ({Link(self.link)}), VDOM: {self.vdom}, Duplex: {Duplex(self.duplex)}, VLAN: {self.vlanid}, IP: {self.ip}/{self.mask}, Parent: {self.interface}"


class VdomData(BaseModel):
    vdom: str
    results: Dict[str, Interface]

    @field_validator("results", mode="before", check_fields=False)
    @classmethod
    def add_vdom_to_interfaces(cls, v, info):
        vdom = info.data.get("vdom")
        if vdom is None:
            return v  # or Optional: raise ValueError("vdom is required")

        for interface in v.values():
            interface["vdom"] = vdom
        return v


class VdomDataList(RootModel):
    root: List[VdomData]


VdomDataList.model_rebuild()


class Link(IntEnum):
    up = True
    down = False

    def __str__(self):
        return self.name


class Duplex(IntEnum):
    DEFAULT = -1
    HALF = 0
    FULL = 1
    UNKNOWN = -1

    def __str__(self):
        return self.name


DISCOVERY_DEFAULT_PARAMETERS = dict({"fortios_interface_excluded": [], "item_discovery_link_status": False, "item_excluded_by_type": "index"})


def parse_fortios_interfaces(string_table):
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    data = VdomDataList.model_validate(json_data)

    combined_results = {}
    for vdom_data in data.root:
        combined_results.update(vdom_data.results)
    return combined_results


register.agent_section(
    name="fortios_interfaces",
    parse_function=parse_fortios_interfaces,
)


def discovery_fortios_interfaces(params: Mapping[str, Any], section_fortios_interfaces, section_fortios_interfaces_cmdb) -> DiscoveryResult:
    item_discovery_by_type = params["item_excluded_by_type"]
    item_discovery_link_status = params["item_discovery_link_status"]

    for item in section_fortios_interfaces:
        interface_name: None
        interface = section_fortios_interfaces.get(item)
        interface_cmdb = section_fortios_interfaces_cmdb.get(interface.id)

        if interface_cmdb:
            interface_name = interface_cmdb.name
            interface.description = interface_cmdb.description
            interface.interface_type = interface_cmdb.type
        else:
            interface_name = interface.id

        if item_discovery_by_type == "descr" and (interface.description) is not None:
            interface_name = interface.description

        elif item_discovery_by_type == "alias" and (interface.alias) is not None:
            interface_name = interface.alias

        if not any(re.search(pattern, interface_name) for pattern in params["fortios_interface_excluded"]):
            if item_discovery_link_status:
                if interface.link:
                    yield Service(item=item)
            else:
                yield Service(item=item)


def check_fortios_interfaces(item: str, section_fortios_interfaces, section_fortios_interfaces_cmdb) -> CheckResult:
    interface = section_fortios_interfaces.get(item)
    if not interface:
        yield Result(state=State.UNKNOWN, summary="Interface %s is missing" % (item))
        return
    if not interface.link:
        yield Result(state=State.CRIT, summary=interface.summary)
    else:
        yield Result(state=State.OK, summary=interface.summary)

    value_store = get_value_store()
    now_time = time.time()

    for key in ["rx_packets", "tx_packets", "if_in_bps", "if_out_bps", "rx_errors", "tx_errors"]:
        if hasattr(interface, key):
            attribute = getattr(interface, key)
            value = 0
            try:
                value = get_rate(value_store, f"{key}", now_time, attribute, raise_overflow=False)
            except GetRateError:
                pass

            yield Metric(name=f"{key}", value=value, boundaries=(0, None))

            if key == "if_in_bps":
                yield from check_levels(
                    value=value / 8,
                    label="In",
                    render_func=networkbandwidth,
                )

            if key == "if_out_bps":
                yield from check_levels(
                    value=value / 8,
                    label="Out",
                    render_func=networkbandwidth,
                )

    yield from check_levels(
        value=interface.speed,
        label="Speed",
        render_func=nicspeed,
    )


register.check_plugin(
    name="fortios_interfaces",
    service_name="Interface %s",
    sections=["fortios_interfaces", "fortios_interfaces_cmdb"],
    discovery_function=discovery_fortios_interfaces,
    discovery_ruleset_name="discovery_fortios_interfaces",
    discovery_default_parameters=DISCOVERY_DEFAULT_PARAMETERS,
    check_function=check_fortios_interfaces,
)
