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

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_managed_switch_health import (
    CPU,
    POE,
    FanSpeed,
    FanSummaryEntry,
    FortiosSwitchData,
    Memory,
    PerformanceStatus,
    Summary,
    SummaryEntry,
    TimeUnit,
    Uptime,
)
from cmk_addons.plugins.fortios.agent_based.fortios_managed_switch_summary import (
    check_fortios_switch_summary,
    discovery_fortios_switch_summary,
)

PerformanceStatus.model_rebuild()

_perf = PerformanceStatus(
    cpu=CPU(idle=TimeUnit(unit="%", value=87), nice=TimeUnit(unit="%", value=0), system=TimeUnit(unit="%", value=12), user=TimeUnit(unit="%", value=1)),
    memory=Memory(used=TimeUnit(unit="%", value=36)),
    uptime=Uptime(days=TimeUnit(unit="days", value=113), hours=TimeUnit(unit="hours", value=5), minutes=TimeUnit(unit="minutes", value=16)),
)
_poe = POE(max_value=800, unit="watts", value=26.1)

_summary_all_good = Summary(
    overall="good",
    cpu=SummaryEntry(value=13, rating="good"),
    memory=SummaryEntry(value=36, rating="good"),
    temperature=SummaryEntry(value=44.0, rating="good"),
    poe=SummaryEntry(value=100.0, rating="good"),
    uptime=SummaryEntry(value=10352160, rating="good"),
    fan={"Fan1": FanSummaryEntry(value="normal", rating="good", fan_speed=FanSpeed(value=50.0, unit="%"))},
    psu={"PSU1": SummaryEntry(value="normal", rating="good")},
)

_summary_with_warning = Summary(
    overall="warning",
    cpu=SummaryEntry(value=13, rating="good"),
    memory=SummaryEntry(value=36, rating="good"),
    temperature=SummaryEntry(value=85.0, rating="warning"),
    poe=SummaryEntry(value=100.0, rating="good"),
    fan={"Fan1": FanSummaryEntry(value="normal", rating="good", fan_speed=FanSpeed(value=50.0, unit="%"))},
    psu={"PSU1": SummaryEntry(value="failed", rating="critical")},
)


def test_discovery_with_summary():
    section = FortiosSwitchData(performance=_perf, poe=_poe, summary=_summary_all_good)
    assert list(discovery_fortios_switch_summary(section)) == [Service()]


def test_discovery_without_summary():
    section = FortiosSwitchData(performance=_perf, poe=_poe)
    assert list(discovery_fortios_switch_summary(section)) == []


def test_check_all_good():
    section = FortiosSwitchData(performance=_perf, poe=_poe, summary=_summary_all_good)
    results = list(check_fortios_switch_summary(section))

    assert Result(state=State.OK, summary="Overall: good") in results
    assert Result(state=State.OK, notice="CPU: good (value: 13)") in results
    assert Result(state=State.OK, notice="Memory: good (value: 36)") in results
    assert Result(state=State.OK, notice="Temperature: good (value: 44.0)") in results
    assert Result(state=State.OK, notice="PoE: good (value: 100.0)") in results
    assert Result(state=State.OK, notice="Fan Fan1: good, speed: 50.0%") in results
    assert Result(state=State.OK, notice="PSU PSU1: good") in results


def test_check_warning_and_critical():
    section = FortiosSwitchData(performance=_perf, poe=_poe, summary=_summary_with_warning)
    results = list(check_fortios_switch_summary(section))

    assert Result(state=State.CRIT, summary="Overall: warning") in results
    assert Result(state=State.WARN, notice="Temperature: warning (value: 85.0)") in results
    assert Result(state=State.CRIT, notice="PSU PSU1: critical") in results


def test_check_no_summary():
    section = FortiosSwitchData(performance=_perf, poe=_poe)
    results = list(check_fortios_switch_summary(section))
    assert results == []
