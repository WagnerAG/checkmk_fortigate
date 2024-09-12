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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)


def discovery_fortios_switch_uptime(section) -> DiscoveryResult:
    yield Service()


def check_fortios_switch_uptime(section: str) -> CheckResult:
    yield Result(state=State.OK, summary=section.uptime_summary)

    yield Metric("uptime", section.get_uptime_in_sec)


register.check_plugin(
    name="fortios_managed_switch_uptime",
    service_name="Uptime",
    sections=["fortios_managed_switch_health"],
    discovery_function=discovery_fortios_switch_uptime,
    check_function=check_fortios_switch_uptime,
)
