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
from collections.abc import Mapping, Sequence
from typing import Optional

from pydantic import BaseModel, model_validator

from cmk.agent_based.v2 import AgentSection


class Proxy(BaseModel):
    port: int
    protocol: int
    protocol_name: str
    subnet: str


class ProxySource(BaseModel):
    expire: Optional[int] = None
    incoming_bytes: Optional[int] = 0
    outgoing_bytes: Optional[int] = 0
    p2name: Optional[str] = None
    p2serial: int
    proxy_dst: Optional[Sequence[Proxy]] = None
    proxy_src: Optional[Sequence[Proxy]] = None
    status: Optional[str] = None


class FortiIPSec(BaseModel):
    name: str
    proxyid: Sequence[ProxySource]
    comments: Optional[str] = None
    connection_count: Optional[int] = 0
    dialup_index: Optional[int] = None
    creation_time: Optional[int] = None
    type: Optional[str] = None
    incoming_bytes: Optional[int] = 0
    outgoing_bytes: Optional[int] = 0
    fct_uid: Optional[str] = None
    parent: Optional[str] = None
    rgwy: Optional[str] = None
    xauth_user: Optional[str] = None
    tun_id: Optional[str] = None  # IPv4
    tun_id6: Optional[str] = None  # IPv6
    username: Optional[str] = None  # IPv4
    tunnels_up: int = 0
    tunnels_down: int = 0
    tunnels_total: int = 0

    @model_validator(mode="after")
    @classmethod
    def count_tunnels_up(cls, model):
        if model.proxyid:
            model.tunnels_up = sum(1 for proxy in model.proxyid if proxy.status == "up")
        return model

    @model_validator(mode="after")
    @classmethod
    def count_tunnels_down(cls, model):
        if model.proxyid:
            model.tunnels_down = sum(1 for proxy in model.proxyid if proxy.status == "down")
        return model

    @model_validator(mode="after")
    @classmethod
    def count_tunnels(cls, model):
        model.tunnels_up = sum(1 for proxy in model.proxyid if proxy.status == "up")
        model.tunnels_total = len(model.proxyid)
        return model

    @property
    def summary(self) -> str:
        return f"Type: {self.type}"


def replace_hyphens(d):
    if isinstance(d, dict):
        new_dict = {}
        for k, v in d.items():
            new_key = k.replace("-", "_")
            new_dict[new_key] = replace_hyphens(v)
        return new_dict
    elif isinstance(d, list):
        return [replace_hyphens(item) for item in d]
    else:
        return d


def parse_fortios_ipsec(string_table) -> Mapping[str, FortiIPSec] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except ValueError:
        json_data = None
    if (forti_ipsec_tunnels := json_data[0].get("results")) in ({}, []):
        return None
    return {item["name"]: FortiIPSec(**item) for item in replace_hyphens(forti_ipsec_tunnels)}


agent_section_fortios_ipsec = AgentSection(
    name="fortios_ipsec",
    parse_function=parse_fortios_ipsec,
)
