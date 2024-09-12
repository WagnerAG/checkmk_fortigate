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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    render,
)
from pydantic import BaseModel


class TimeUnit(BaseModel):
    unit: str
    value: int


class PerformanceStatus(BaseModel):
    cpu: CPU
    memory: Memory
    uptime: Uptime


class CPU(BaseModel):
    idle: TimeUnit
    nice: TimeUnit
    system: TimeUnit
    user: TimeUnit


class Memory(BaseModel):
    used: TimeUnit


class Uptime(BaseModel):
    days: TimeUnit
    hours: TimeUnit
    minutes: TimeUnit


class POE(BaseModel):
    max_value: int
    unit: str
    value: float


class FortiosSwitchData(BaseModel):
    performance_status: PerformanceStatus
    poe: POE

    @property
    def cpu_summary(self):
        total_cpu = 100 - self.performance_status.cpu.idle.value
        return f"Total CPU: {total_cpu}%, nice: {self.performance_status.cpu.nice.value}%, system: {self.performance_status.cpu.system.value}%, user: {self.performance_status.cpu.user.value}%"

    @property
    def memory_summary(self):
        return f"Total Memory: {self.performance_status.memory.used.value}%"

    @property
    def poe_summary(self):
        if self.poe.max_value == 0.0:
            return "This Switch is not POE capable"
        else:
            return f"POE usage ({self.poe.value:.2f}W/{self.poe.max_value:.2f}W) {render.percent((self.poe.value/self.poe.max_value)*100)}"

    @property
    def uptime_summary(self):
        return f"Uptime: {self.performance_status.uptime.days.value} days, {self.performance_status.uptime.hours.value} hours, {self.performance_status.uptime.minutes.value} minutes"

    @property
    def get_uptime_in_sec(self):
        minutes = self.performance_status.uptime.minutes.value * 60
        hours = self.performance_status.uptime.hours.value * 60 * 60
        days = self.performance_status.uptime.days.value * 60 * 60 * 24

        return minutes + hours + days


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


def parse_fortios_managed_switch_health(string_table) -> FortiosSwitchData | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError):
        return None

    if (switch_health := replace_hyphens(json_data)) is None:
        return None

    PerformanceStatus.update_forward_refs()
    return FortiosSwitchData(**switch_health)


register.agent_section(
    name="fortios_managed_switch_health",
    parse_function=parse_fortios_managed_switch_health,
)
