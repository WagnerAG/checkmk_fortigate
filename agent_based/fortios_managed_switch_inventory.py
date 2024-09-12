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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    TableRow,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import InventoryResult

from .fortios_managed_switch import Switch


def model_version_build(os_version: str) -> tuple[str, str, str]:
    if os_version:
        try:
            model, version, build = os_version.split("-")
        except ValueError:
            model = os_version
            version = os_version
            build = os_version
    else:
        model = ""
        version = ""
        build = ""
    return model, version, build


def inventory_fortios_managed_switch(section: Switch) -> InventoryResult:
    if section is None:
        return

    path = ["networking", "fortios", "switches"]
    for _k, v in section.items():
        model, version, build = model_version_build(v.os_version)
        yield TableRow(path=path, key_columns={"name": v.name, "serial": v.serial, "model": model, "version": version, "build": build})


register.inventory_plugin(
    name="fortios_managed_switch",
    inventory_function=inventory_fortios_managed_switch,
)
