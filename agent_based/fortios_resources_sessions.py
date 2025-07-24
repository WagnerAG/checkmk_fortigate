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

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    Service,
    State,
    check_levels,
    register,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .fortios_resources import FortiResource

DEFAULT_SESSION_LEVELS: Dict = {"session_levels": (20000, 30000)}


def discovery_fortios_resources_sessions(section: FortiResource) -> DiscoveryResult:
    yield Service()


def check_fortios_resources_sessions(params: Mapping[str, Any], section: FortiResource) -> CheckResult:
    session_levels = params.get("session_levels")

    yield Result(state=State.OK, summary="Sessions")
    yield Metric("active_sessions", section.total_sessions, levels=session_levels)
    yield from check_levels(
        metric_name="total_sessions",
        value=section.total_sessions,
        levels_upper=session_levels,
        label="Total",
        boundaries=(0, None),
    )

    if len(section.vdoms) > 1:
        for item in section.vdoms:
            yield Metric(item.vdom, item.results.session.current_usage, boundaries=(0, 100))


register.check_plugin(
    name="fortios_resources_sessions",
    service_name="Sessions",
    sections=["fortios_vdom_resources"],
    discovery_function=discovery_fortios_resources_sessions,
    check_ruleset_name="fortios_resources_sessions",
    check_function=check_fortios_resources_sessions,
    check_default_parameters=DEFAULT_SESSION_LEVELS,
)
