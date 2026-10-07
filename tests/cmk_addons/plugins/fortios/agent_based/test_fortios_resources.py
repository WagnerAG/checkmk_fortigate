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

from cmk_addons.plugins.fortios.agent_based.fortios_resources import (
    FortiResource,
    ResourceUsage,
    UsageSample,
    parse_fortios_resources,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"http_method": "GET", "name": "usage", "path": "system/resource", "results": {"cpu": [{"current": 0}], "mem": [{"current": 46}], "session": [{"current": 1344}]}, "serial": "Serial01", "status": "success"}'
                ]
            ],
            [FortiResource(results=ResourceUsage(cpu=[UsageSample(current=0)], mem=[UsageSample(current=46)], session=[UsageSample(current=1344)]), total_cpu=0, total_memory=46, total_sessions=1344)],
        ),
    ],
)
def test_parse_fortios_resource(string_table, expected_section) -> None:
    assert parse_fortios_resources(string_table) == expected_section[0]
