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
from cmk.base.plugins.agent_based.fortios_resources import FortiResource, Resource, ResourceResult, Session, parse_fortios_resources


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '[{"action": "", "build": 1639, "http_method": "GET", "name": "vdom-resource", "path": "system", "results": {"cpu": 0, "custom-service": {"current_usage": 122, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 9, "max_custom_value": 2048, "max_guaranteed_value": 2048, "min_custom_value": 122, "min_guaranteed_value": 0, "usage_percent": 0}, "dialup-tunnel": {"current_usage": 4, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 5, "max_custom_value": 0, "max_guaranteed_value": 0, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "firewall-address": {"current_usage": 78, "custom_max": 0, "global_max": 42048, "guaranteed": 0, "id": 7, "max_custom_value": 42048, "max_guaranteed_value": 42048, "min_custom_value": 78, "min_guaranteed_value": 0, "usage_percent": 0}, "firewall-addrgrp": {"current_usage": 7, "custom_max": 0, "global_max": 10692, "guaranteed": 0, "id": 8, "max_custom_value": 10692, "max_guaranteed_value": 10692, "min_custom_value": 7, "min_guaranteed_value": 0, "usage_percent": 0}, "firewall-policy": {"current_usage": 44, "custom_max": 0, "global_max": 21024, "guaranteed": 0, "id": 6, "max_custom_value": 20640, "max_guaranteed_value": 20640, "min_custom_value": 44, "min_guaranteed_value": 0, "usage_percent": 0}, "ipsec-phase1": {"current_usage": 0, "custom_max": 0, "global_max": 2000, "guaranteed": 0, "id": 1, "max_custom_value": 2000, "max_guaranteed_value": 2000, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "ipsec-phase1-interface": {"current_usage": 4, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 3, "max_custom_value": 0, "max_guaranteed_value": 0, "min_custom_value": 4, "min_guaranteed_value": 0, "usage_percent": 0}, "ipsec-phase2": {"current_usage": 0, "custom_max": 0, "global_max": 2000, "guaranteed": 0, "id": 2, "max_custom_value": 2000, "max_guaranteed_value": 2000, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "ipsec-phase2-interface": {"current_usage": 4, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 4, "max_custom_value": 0, "max_guaranteed_value": 0, "min_custom_value": 4, "min_guaranteed_value": 0, "usage_percent": 0}, "is_deletable": false, "log-disk-quota": {"current_usage": 0, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 17, "max_custom_value": 0, "max_guaranteed_value": 0, "min_custom_value": 100, "min_guaranteed_value": 0, "usage_percent": 0}, "memory": 46, "onetime-schedule": {"current_usage": 0, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 11, "max_custom_value": 1000, "max_guaranteed_value": 1000, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "proxy": {"current_usage": 0, "custom_max": 0, "global_max": 12000, "guaranteed": 0, "id": 16, "max_custom_value": 12000, "max_guaranteed_value": 12000, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "recurring-schedule": {"current_usage": 2, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 12, "max_custom_value": 512, "max_guaranteed_value": 512, "min_custom_value": 2, "min_guaranteed_value": 0, "usage_percent": 0}, "service-group": {"current_usage": 8, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 10, "max_custom_value": 1000, "max_guaranteed_value": 1000, "min_custom_value": 8, "min_guaranteed_value": 0, "usage_percent": 0}, "session": {"current_usage": 1344, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 0, "max_custom_value": 0, "max_guaranteed_value": 0, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "setup_rate": 10, "sslvpn": {"current_usage": 0, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 15, "max_custom_value": 0, "max_guaranteed_value": 0, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "user": {"current_usage": 0, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 13, "max_custom_value": 1000, "max_guaranteed_value": 1000, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}, "user-group": {"current_usage": 0, "custom_max": 0, "global_max": 0, "guaranteed": 0, "id": 14, "max_custom_value": 500, "max_guaranteed_value": 500, "min_custom_value": 1, "min_guaranteed_value": 0, "usage_percent": 0}}, "serial": "Serial01", "status": "success", "vdom": "root", "version": "v7.2.8"}]'
                ]
            ],
            [FortiResource(vdoms=[ResourceResult(results=Resource(cpu=0, memory=46, session=Session(current_usage=1344)), vdom="root")], total_cpu=0, total_memory=46, total_sessions=1344)],
        ),
    ],
)
def test_parse_fortios_resource(string_table, expected_section) -> None:
    assert parse_fortios_resources(string_table) == expected_section[0]
