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
    register,
)
from pydantic import BaseModel


class DhcpLease(BaseModel):
    ip: Optional[str]
    reserved: bool
    mac: Optional[str]
    vci: Optional[str]
    hostname: Optional[str]
    expire_time: Optional[int]
    status: Optional[str]
    interface: Optional[str]
    type: Optional[str]
    server_mkey: int
    server_ipam_enabled: bool


def parse_fortios_dhcp_lease(string_table) -> Mapping[str, DhcpLease] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (forti_dhcp_lease := json_data.get("results")) in ({}, []):
        return None

    return {item["mac"]: DhcpLease(**item) for item in forti_dhcp_lease}


register.agent_section(
    name="fortios_dhcp_lease",
    parse_function=parse_fortios_dhcp_lease,
)
