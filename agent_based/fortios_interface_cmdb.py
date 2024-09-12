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
from typing import List, Optional

from cmk.base.plugins.agent_based.agent_based_api.v1 import register
from pydantic import BaseModel


class InterfaceCMDB(BaseModel):
    algorithm: Optional[str]
    alias: str  # Needed
    allowaccess: Optional[str]
    arpforward: Optional[str]
    bfd: Optional[str]
    defaultgw: Optional[str]
    description: str # Needed
    detectprotocol: Optional[str]
    detectserver: Optional[str]
    devindex: Optional[int]
    distance: Optional[int]
    external: Optional[str]
    gwdetect: Optional[str]
    inbandwidth: Optional[int]
    interface: str # Needed
    internal: Optional[str]
    ip: Optional[str]
    ipmac: Optional[str]
    ipunnumbered: Optional[str]
    macaddr: str # Needed
    mode: str # Needed
    mtu: Optional[int]
    name: str # Needed
    ndiscforward: Optional[str]
    outbandwidth: Optional[int]
    password: Optional[str]
    priority: Optional[int]
    q_origin_key: str # Needed
    role: Optional[str]
    speed: Optional[str]
    status: Optional[str]
    stp: Optional[str]
    stpforward: Optional[str]
    subst: Optional[str]
    tagging: List[str]
    trunk: Optional[str]
    type: str # Needed
    username: Optional[str]
    vdom: Optional[str]
    vindex: Optional[int]
    vlanforward: Optional[str]
    vlanid: Optional[int]
    vrf: Optional[int]
    wccp: Optional[str]
    weight: Optional[int]


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
