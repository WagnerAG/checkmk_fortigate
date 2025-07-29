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

from cmk.base.plugins.agent_based.agent_based_api.v1 import register
from pydantic import BaseModel


class InterfaceCMDB(BaseModel):
    alias: str
    description: str = ""
    interface: str
    macaddr: str
    mode: str
    name: str
    q_origin_key: str
    type: str


def parse_fortios_interfaces_cmdb(string_table):
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (interface_data := json_data.get("results")) is None:
        return None

    return {interface["name"]: InterfaceCMDB(**interface) for interface in interface_data}


register.agent_section(
    name="fortios_interfaces_cmdb",
    parse_function=parse_fortios_interfaces_cmdb,
)
