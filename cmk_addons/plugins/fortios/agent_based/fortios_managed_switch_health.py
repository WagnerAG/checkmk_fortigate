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

from pydantic import BaseModel


from cmk.agent_based.v2 import AgentSection, render


class TimeUnit(BaseModel):
    unit: str
    value: int


class PerformanceStatus(BaseModel):
    cpu: CPU
    memory: Memory
    uptime: Uptime
    network: dict | None = None  # 7.4+ only, not used in checks


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


class SummaryEntry(BaseModel):
    value: int | float | str | None = None
    rating: str


class FanSpeed(BaseModel):
    value: float
    unit: str


class FanSummaryEntry(BaseModel):
    value: str | None = None
    rating: str
    fan_speed: FanSpeed | None = None


class Summary(BaseModel):
    overall: str | None = None
    cpu: SummaryEntry | None = None
    memory: SummaryEntry | None = None
    temperature: SummaryEntry | None = None
    poe: SummaryEntry | None = None
    uptime: SummaryEntry | None = None
    fan: dict[str, FanSummaryEntry] | None = None
    psu: dict[str, SummaryEntry] | None = None


class FortiosSwitchData(BaseModel):
    # FortiOS 7.4+: field is "performance" (new health-status endpoint)
    performance: PerformanceStatus | None = None
    # FortiOS 7.2: field is "performance-status" → after replace_hyphens: "performance_status"
    performance_status: PerformanceStatus | None = None
    poe: POE
    summary: Summary | None = None

    @property
    def perf(self) -> PerformanceStatus:
        return self.performance or self.performance_status

    @property
    def cpu_summary(self):
        total_cpu = 100 - self.perf.cpu.idle.value
        return f"Total CPU: {total_cpu}%, nice: {self.perf.cpu.nice.value}%, system: {self.perf.cpu.system.value}%, user: {self.perf.cpu.user.value}%"

    @property
    def memory_summary(self):
        return f"Total Memory: {self.perf.memory.used.value}%"

    @property
    def poe_summary(self):
        if self.poe.max_value == 0.0:
            return "This Switch is not POE capable"
        else:
            return f"POE usage ({self.poe.value:.2f}W/{self.poe.max_value:.2f}W) {render.percent((self.poe.value / self.poe.max_value) * 100)}"

    @property
    def uptime_summary(self):
        return f"Uptime: {self.perf.uptime.days.value} days, {self.perf.uptime.hours.value} hours, {self.perf.uptime.minutes.value} minutes"

    @property
    def get_uptime_in_sec(self):
        minutes = self.perf.uptime.minutes.value * 60
        hours = self.perf.uptime.hours.value * 60 * 60
        days = self.perf.uptime.days.value * 60 * 60 * 24

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

    PerformanceStatus.model_rebuild()
    return FortiosSwitchData(**switch_health)


agent_section_fortios_managed_switch_health = AgentSection(
    name="fortios_managed_switch_health",
    parse_function=parse_fortios_managed_switch_health,
)
