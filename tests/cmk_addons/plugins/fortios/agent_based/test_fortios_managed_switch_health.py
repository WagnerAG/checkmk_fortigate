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

from cmk_addons.plugins.fortios.agent_based.fortios_managed_switch_health import (
    FortiosSwitchData,
    parse_fortios_managed_switch_health,
    replace_hyphens,
)


@pytest.fixture
def valid_json_legacy():
    """FortiOS 7.2 format: field name is 'performance-status'"""
    return """{
        "performance-status": {
            "cpu": {
                "idle": {"unit": "%", "value": 86},
                "nice": {"unit": "%", "value": 0},
                "system": {"unit": "%", "value": 13},
                "user": {"unit": "%", "value": 1}
            },
            "memory": {"used": {"unit": "%", "value": 36}},
            "uptime": {
                "days": {"unit": "days", "value": 109},
                "hours": {"unit": "hours", "value": 17},
                "minutes": {"unit": "minutes", "value": 3}
            }
        },
        "poe": {
            "max_value": 800,
            "unit": "watts",
            "value": 25.9
        }
    }"""


@pytest.fixture
def valid_json_new():
    """FortiOS 7.4+ format: field name is 'performance', includes extra fields"""
    return """{
        "serial": "FSWTESTSERIAL001",
        "switch-id": "FSWTESTSERIAL001",
        "performance": {
            "cpu": {
                "idle": {"unit": "%", "value": 86},
                "nice": {"unit": "%", "value": 0},
                "system": {"unit": "%", "value": 13},
                "user": {"unit": "%", "value": 1}
            },
            "memory": {"used": {"unit": "%", "value": 36}},
            "network": {
                "in-1min": {"unit": "kbps", "value": 0},
                "in-10min": {"unit": "kbps", "value": 0},
                "in-30min": {"unit": "kbps", "value": 0}
            },
            "uptime": {
                "days": {"unit": "days", "value": 109},
                "hours": {"unit": "hours", "value": 17},
                "minutes": {"unit": "minutes", "value": 3}
            }
        },
        "poe": {
            "max_value": 800,
            "unit": "watts",
            "value": 25.9
        },
        "fan": [],
        "psu": []
    }"""


# keep old fixture name as alias so parametrized tests still work
@pytest.fixture
def valid_json(valid_json_legacy):
    return valid_json_legacy


def test_replace_hyphens():
    input_data = {
        "performance-status": {
            "cpu": {
                "cpu_idle": {"cpu-unit": "%", "cpu-value": 86},
            }
        }
    }
    expected_output = {
        "performance_status": {
            "cpu": {
                "cpu_idle": {"cpu_unit": "%", "cpu_value": 86},
            }
        }
    }
    assert replace_hyphens(input_data) == expected_output


def test_parse_fortios_managed_switch_health_legacy(valid_json_legacy):
    parsed_data = parse_fortios_managed_switch_health([[valid_json_legacy]])
    assert isinstance(parsed_data, FortiosSwitchData)
    assert parsed_data.perf.cpu.idle.value == 86
    assert parsed_data.perf.memory.used.value == 36
    assert parsed_data.poe.max_value == 800
    assert parsed_data.poe.value == 25.9


def test_parse_fortios_managed_switch_health_new(valid_json_new):
    parsed_data = parse_fortios_managed_switch_health([[valid_json_new]])
    assert isinstance(parsed_data, FortiosSwitchData)
    assert parsed_data.perf.cpu.idle.value == 86
    assert parsed_data.perf.memory.used.value == 36
    assert parsed_data.poe.max_value == 800
    assert parsed_data.poe.value == 25.9


def test_invalid_json():
    string_table = [["{invalid_json}"]]
    parsed_data = parse_fortios_managed_switch_health(string_table)
    assert parsed_data is None


def test_cpu_summary(valid_json):
    parsed_data = parse_fortios_managed_switch_health([[valid_json]])
    assert parsed_data.cpu_summary == "Total CPU: 14%, nice: 0%, system: 13%, user: 1%"


def test_memory_summary(valid_json):
    parsed_data = parse_fortios_managed_switch_health([[valid_json]])
    assert parsed_data.memory_summary == "Total Memory: 36%"


def test_poe_summary(valid_json):
    parsed_data = parse_fortios_managed_switch_health([[valid_json]])
    assert parsed_data.poe_summary == "POE usage (25.90W/800.00W) 3.24%"


def test_uptime_summary(valid_json):
    parsed_data = parse_fortios_managed_switch_health([[valid_json]])
    assert parsed_data.uptime_summary == "Uptime: 109 days, 17 hours, 3 minutes"


def test_get_uptime_in_sec(valid_json):
    parsed_data = parse_fortios_managed_switch_health([[valid_json]])
    assert parsed_data.get_uptime_in_sec == (109 * 24 * 60 * 60 + 17 * 60 * 60 + 3 * 60)
