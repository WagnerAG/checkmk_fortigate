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
from cmk.base.plugins.agent_based.fortios_managed_switch import Switch, parse_fortios_managed_switch


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"action": "status", "build": 1639, "http_method": "GET", "name": "managed-switch", "path": "switch-controller", "results": [{"connecting_from": "10.10.1.1", "dhcp_snooping_supported": true, "fgt_peer_intf_name": "fortilink", "igmp_snooping_supported": true, "image_download_progress": 0, "is_l3": false,"join_time": "Thu Mar  7 13:29:08 2024", "led_blink_supported": true, "max_poe_budget": 800, "mc_lag_supported": true, "name": "Switch01", "os_version": "S448EF-v7.2.4-build444,230317 (GA)", "ports": [{"dhcp_snooping": {"untrusted": 0}, "duplex": "full", "fgt_peer_device_name": "", "fgt_peer_port_name": "", "fortilink_port": false, "igmp_snooping_group": {"group_count": 0}, "interface": "port48", "isl_peer_device_name": "", "isl_peer_port_name": "", "isl_peer_trunk_name": "", "mclag": false, "mclag_icl": false, "poe_capable": true, "poe_status": "enabled", "port_power": 6.300000190734863, "power_status": 2, "speed": 1000, "status": "up", "vlan": "MGMT"}], "serial": "S448EFTF23007664", "state": "Authorized", "status": "Connected", "type": "physical", "vdom": "root"}]}'
                ]
            ],
            [{"Switch01": Switch(status="Connected", name="Switch01", serial="S448EFTF23007664", state="Authorized", fgt_peer_intf_name="fortilink", connecting_from="10.10.1.1", join_time="Thu Mar  7 13:29:08 2024", type="physical", is_l3="False", max_poe_budget=800, igmp_snooping_supported=True, dhcp_snooping_supported=True, mc_lag_supported=True, led_blink_supported=True, os_version="S448EF-v7.2.4-build444,230317 (GA)")}],
        ),
    ],
)
def test_parse_fortios_managed_switch(string_table, expected_section) -> None:
    assert parse_fortios_managed_switch(string_table) == expected_section[0]
