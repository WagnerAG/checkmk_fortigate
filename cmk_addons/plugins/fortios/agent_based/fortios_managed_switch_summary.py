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

from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State


def _rating_to_state(rating: str) -> State:
    match rating.lower():
        case "good":
            return State.OK
        case "warning":
            return State.WARN
        case _:
            return State.CRIT


def discovery_fortios_switch_summary(section) -> DiscoveryResult:
    if section and section.summary:
        yield Service()


def check_fortios_switch_summary(section) -> CheckResult:
    if not section or not section.summary:
        return

    summary = section.summary
    component_states = []

    scalar_entries = {
        "CPU": summary.cpu,
        "Memory": summary.memory,
        "Temperature": summary.temperature,
        "PoE": summary.poe,
    }

    for label, entry in scalar_entries.items():
        if entry is None:
            continue
        state = _rating_to_state(entry.rating)
        component_states.append(state)
        yield Result(state=state, notice=f"{label}: {entry.rating} (value: {entry.value})")

    if summary.fan:
        for fan_name, fan_entry in summary.fan.items():
            state = _rating_to_state(fan_entry.rating)
            component_states.append(state)
            speed = f", speed: {fan_entry.fan_speed.value}{fan_entry.fan_speed.unit}" if fan_entry.fan_speed else ""
            yield Result(state=state, notice=f"Fan {fan_name}: {fan_entry.rating}{speed}")

    if summary.psu:
        for psu_name, psu_entry in summary.psu.items():
            state = _rating_to_state(psu_entry.rating)
            component_states.append(state)
            yield Result(state=state, notice=f"PSU {psu_name}: {psu_entry.rating}")

    overall_rating = summary.overall or "unknown"
    worst = max(component_states, key=lambda s: s.value, default=State.OK)
    yield Result(state=worst, summary=f"Overall: {overall_rating}")


check_plugin_fortios_managed_switch_summary = CheckPlugin(
    name="fortios_managed_switch_summary",
    service_name="Health Summary",
    sections=["fortios_managed_switch_health"],
    discovery_function=discovery_fortios_switch_summary,
    check_function=check_fortios_switch_summary,
)
