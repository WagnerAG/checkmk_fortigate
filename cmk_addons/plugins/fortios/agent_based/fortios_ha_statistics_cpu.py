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

from typing import Any, Dict, Mapping

from cmk.agent_based.v1 import check_levels
from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Metric, Result, Service, State
from cmk.agent_based.v2.render import percent

from .fortios_ha_statistics import HAStatistics

DEFAULT_CPU_LEVELS: Dict = {"util": (80.0, 90.0)}


def discovery_fortios_ha_statistics_cpu(section: HAStatistics) -> DiscoveryResult:
    for node in section.nodes:
        yield Service(item=node.hostname)


def check_fortios_ha_statistics_cpu(item: str, params: Mapping[str, Any], section: HAStatistics) -> CheckResult:
    node = section.node(item)
    if node is None:
        yield Result(state=State.UNKNOWN, summary="No data available for this node")
        return

    cpu_levels = params.get("util")

    yield Metric("util", node.cpu_usage, levels=cpu_levels, boundaries=(0, 100))
    yield from check_levels(
        value=node.cpu_usage,
        label="CPU load",
        metric_name="util",
        levels_upper=cpu_levels,
        render_func=percent,
        boundaries=(0, 100),
    )


check_plugin_fortios_ha_statistics_cpu = CheckPlugin(
    name="fortios_ha_statistics_cpu",
    service_name="CPU utilization %s",
    sections=["fortios_ha_statistics"],
    discovery_function=discovery_fortios_ha_statistics_cpu,
    check_ruleset_name="cpu_utilization",
    check_function=check_fortios_ha_statistics_cpu,
    check_default_parameters=DEFAULT_CPU_LEVELS,
)
