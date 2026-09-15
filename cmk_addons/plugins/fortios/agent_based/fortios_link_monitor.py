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

FortiGate link monitors (SD-WAN health checks)

"""

from __future__ import annotations

import json
from typing import Any, Mapping

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
    render,
)
from pydantic import BaseModel


class LinkMonitor(BaseModel):
    name: str
    label: str
    state: str
    latency: float
    jitter: float
    packet_loss: float
    vdom: str | None = None

    @property
    def is_alive(self) -> bool:
        return self.state == "alive"

    @property
    def is_disabled(self) -> bool:
        return self.state == "disabled"

    @property
    def summary(self) -> str:
        summary = f"Link monitor is {self.state}"
        if self.vdom:
            summary += f", VDOM: {self.vdom}"
        return summary


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _members(data: Any) -> list[Mapping[str, Any]]:
    """Extract the individual monitored servers/interfaces from a link monitor or SD-WAN health-check entry.

    Depending on the FortiOS feature and version, a monitor entry is either a dict keyed by
    server IP (classic "config system link-monitor"), a list of interface members (SD-WAN
    health-check, "diagnose sys sdwan health-check"), or that list nested under a sub key.
    """
    if isinstance(data, list):
        return [member for member in data if isinstance(member, dict)]
    if isinstance(data, dict):
        if data and all(isinstance(value, dict) for value in data.values()):
            # classic format: keyed by server IP, keep the key as label
            return [{"_key": key, **value} for key, value in data.items()]
        for key in ("children", "members", "results"):
            nested = data.get(key)
            if isinstance(nested, list):
                return [member for member in nested if isinstance(member, dict)]
        return [data]
    return []


def _member_label(member: Mapping[str, Any], index: int) -> str:
    for key in ("_key", "interface", "server", "ip", "host", "address"):
        if member.get(key):
            return str(member[key])
    return str(member.get("seq", index))


def _member_status(member: Mapping[str, Any]) -> str:
    return str(member.get("status", member.get("state", "alive")))


def _parse_members(name: str, vdom: str | None, data: Any) -> list[LinkMonitor]:
    """A link monitor/health-check holds one entry per monitored server or interface; each one
    becomes its own service, so a health-check spanning e.g. 2 WAN interfaces is visible as 2 services"""
    members = _members(data) or [{}]

    link_monitors = []
    for index, member in enumerate(members, start=1):
        status = _member_status(member).lower()
        if status in ("disable", "disabled"):
            state = "disabled"
        elif status in ("up", "alive"):
            state = "alive"
        else:
            state = "dead"

        link_monitors.append(
            LinkMonitor(
                name=name,
                label=_member_label(member, index),
                state=state,
                latency=_float(member.get("latency")),
                jitter=_float(member.get("jitter")),
                packet_loss=_float(member.get("packet_loss", member.get("packet-loss"))),
                vdom=vdom,
            )
        )
    return link_monitors


def parse_fortios_link_monitor(string_table: StringTable) -> Mapping[str, LinkMonitor] | None:
    # (name, vdom) -> accumulated members; SD-WAN health-checks may list one entry per
    # monitored interface, so multiple entries sharing the same name/vdom have to be merged
    grouped: dict[tuple[str, str | None], list[Mapping[str, Any]]] = {}

    for line in string_table:
        try:
            json_data = json.loads(line[0])
        except (ValueError, IndexError):
            continue

        # with 'vdom=*' the API answers with one result set per VDOM
        result_sets = json_data if isinstance(json_data, list) else [json_data]

        for result_set in result_sets:
            if not isinstance(result_set, dict):
                continue
            vdom = result_set.get("vdom")
            results = result_set.get("results")

            if isinstance(results, dict):
                entries = results.items()
            elif isinstance(results, list):
                entries = ((entry.get("name"), entry) for entry in results if isinstance(entry, dict))
            else:
                entries = []

            for name, data in entries:
                if not name or not data:
                    continue
                grouped.setdefault((name, vdom), []).extend(_members(data))

    section: dict[str, LinkMonitor] = {}
    for (name, vdom), members in grouped.items():
        for link_monitor in _parse_members(name, vdom, members):
            item = f"{name} over {link_monitor.label}"
            if item in section:
                # disambiguate identical name/interface combinations reported by different VDOMs
                item = f"{item} ({vdom})" if vdom else item
            section[item] = link_monitor

    return section or None


agent_section_fortios_link_monitor = AgentSection(
    name="fortios_link_monitor",
    parse_function=parse_fortios_link_monitor,
)


def discovery_fortios_link_monitor(section: Mapping[str, LinkMonitor]) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_fortios_link_monitor(item: str, params: Mapping[str, Any], section: Mapping[str, LinkMonitor]) -> CheckResult:
    if not (link_monitor := section.get(item)):
        return

    if link_monitor.is_disabled:
        state = State(params.get("state_disabled", State.WARN.value))
    elif link_monitor.is_alive:
        state = State.OK
    else:
        state = State(params.get("state_dead", State.CRIT.value))

    yield Result(state=state, summary=link_monitor.summary)

    yield from check_levels(
        value=link_monitor.latency,
        levels_upper=params.get("latency_levels"),
        metric_name="latency",
        render_func=lambda v: f"{v:.2f} ms",
        boundaries=(0, None),
        label="Latency",
        notice_only=True,
    )
    yield from check_levels(
        value=link_monitor.jitter,
        levels_upper=params.get("jitter_levels"),
        metric_name="jitter",
        render_func=lambda v: f"{v:.2f} ms",
        boundaries=(0, None),
        label="Jitter",
        notice_only=True,
    )
    yield from check_levels(
        value=link_monitor.packet_loss,
        levels_upper=params.get("packet_loss_levels"),
        metric_name="pl",
        render_func=render.percent,
        boundaries=(0, 100),
        label="Packet loss",
        notice_only=True,
    )


check_plugin_fortios_link_monitor = CheckPlugin(
    name="fortios_link_monitor",
    service_name="Link %s",
    discovery_function=discovery_fortios_link_monitor,
    check_function=check_fortios_link_monitor,
    check_ruleset_name="fortios_link_monitor",
    check_default_parameters={},
)
