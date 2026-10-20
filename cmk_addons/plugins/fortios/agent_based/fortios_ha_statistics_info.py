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

from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Metric, Result, Service, State, render

from .fortios_ha_statistics import HAStatistics


def discovery_fortios_ha_statistics(section: HAStatistics) -> DiscoveryResult:
    for node in section.nodes:
        yield Service(item=node.hostname)


def check_fortios_ha_statistics(item: str, section: HAStatistics) -> CheckResult:
    node = section.node(item)
    if node is None:
        yield Result(state=State.UNKNOWN, summary="No data available for this node")
        return

    summary = (
        f"Serial: {node.serial_no}, "
        f"Uptime: {render.timespan(node.uptime) if node.uptime else 'unknown'}, "
        f"Throughput: {render.bytes(node.tbyte or 0)}, "
        f"Packets: {node.tpacket or 0}"
    )

    details_lines = [
        summary,
        f"Network usage: {node.net_usage}%, Virus scan usage: {node.vir_usage}%, Interrupt usage: {node.intr_usage}%",
    ]
    for vdom in node.per_vdom_stats:
        details_lines.append(f"VDOM {vdom.vdom}: CPU {vdom.cpu_usage}%, Memory {vdom.mem_usage}%, Sessions {vdom.sessions}")

    yield Result(state=State.OK, summary=summary, details="\n".join(details_lines))

    yield Metric("net_usage", node.net_usage or 0, boundaries=(0, 100))
    yield Metric("vir_usage", node.vir_usage or 0, boundaries=(0, 100))
    yield Metric("intr_usage", node.intr_usage or 0, boundaries=(0, 100))


check_plugin_fortios_ha_statistics = CheckPlugin(
    name="fortios_ha_statistics",
    service_name="HA statistics %s",
    discovery_function=discovery_fortios_ha_statistics,
    check_function=check_fortios_ha_statistics,
)
