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
from typing import Mapping, Optional

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Attributes,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import InventoryResult
from pydantic import BaseModel


class ModelInfo(BaseModel):
    hostname: str
    model_name: str
    model: str
    model_number: str


class DeviceInfo(BaseModel):
    serial: str
    version: str
    build: str
    results: Optional[ModelInfo] = None


_MANUFACTURER = "Fortinet"


def parse_fortios_device_info(string_table) -> Mapping[str, DeviceInfo] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (device_info := json_data.get("results")) in ({}, []):
        return None

    return {device_info["hostname"]: DeviceInfo(**json_data)}


register.agent_section(
    name="fortios_device_info",
    parse_function=parse_fortios_device_info,
)


def inventory_fortios_device_info(section: DeviceInfo) -> InventoryResult:
    if section is None:
        return

    path = ["hardware", "system"]
    for _k, v in section.items():
        yield Attributes(path=path, inventory_attributes={"manufacturer": _MANUFACTURER, "serial": v.serial, "product": v.results.model_name, "model": v.results.model})

    path = ["software", "os"]
    for _k, v in section.items():
        yield Attributes(path=path, inventory_attributes={"version": v.version, "build": v.build})


register.inventory_plugin(
    name="fortios_device_info",
    inventory_function=inventory_fortios_device_info,
)
