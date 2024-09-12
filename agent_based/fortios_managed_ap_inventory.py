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

from .fortios_managed_ap import AccessPoint


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


def inventory_fortios_managed_ap(section: AccessPoint) -> InventoryResult:
    if section is None:
        return

    for _k, v in section.items():
        ap_name = str(v.name).replace(" ", "")

        path = ["networking", "fortios", "accesspoints"]
        model, version, build = model_version_build(v.os_version)
        yield TableRow(path=path, key_columns={"name": v.name}, inventory_columns={"ip_addr": v.local_ipv4_addr, "serial": v.serial, "model": model, "version": version, "build": build})

        path = [
            "networking",
            "fortios",
            "accesspoints",
            "lldp",
        ]
        for lldp_value in v.lldp:
            yield TableRow(
                path=path + [ap_name],
                key_columns={"local_port": lldp_value.local_port},
                inventory_columns={"local_port_description": lldp_value.port_description, "switch_name": lldp_value.system_name, "switch_description": lldp_value.system_description, "switch_port": lldp_value.port_id},
            )


register.inventory_plugin(
    name="fortios_managed_ap",
    inventory_function=inventory_fortios_managed_ap,
)
