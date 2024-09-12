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

from datetime import datetime, timedelta
from typing import Tuple
from unittest.mock import patch

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from cmk.base.plugins.agent_based.fortios_managed_ap import LLDP, AccessPoint, AccessPointHealth, GeneralHealth, HealthMetric, Radio, SSIDRadio, WiredInterface, check_fortios_managed_ap, parse_fortios_managed_ap

AP_SECTION: dict = {
    "AP-NAME": AccessPoint(
        name="AP-NAME",
        serial="Serial01",
        status="connected",
        state="authorized",
        clients=1,
        local_ipv4_addr="10.128.0.1",
        board_mac="00:00:00:00:00:00",
        last_reboot_time="04/04/23 15:28",
        ssid=[SSIDRadio(radio=1, list=["Business", "Guest", "IoT"]), SSIDRadio(radio=2, list=["Business", "Guest", "IoT"])],
        lldp=[LLDP(local_port="lan1", chassis_id="mac 00:00:00:00:00:00", system_name="switch01", system_description="FortiSwitch-448E-FPOE v7.2.x,build0000,000000 (GA)", capability="Bridge Router ", port_id="port48", port_description="port48", mau_operating_mode="1000BaseTFD - Four-pair Category 5 UTP, full duplex mode", ip="10.128.1.1", vlan=-1)],
        lldp_enable=True,
        os_version="FP231F-v7.0-build0134",
        radio=[
            Radio(
                radio_id=1,
                mode="AP",
                all_ssids=True,
                auto_txpower=False,
                background_scan_enabled=False,
                bandwidth_rx=0,
                bandwidth_tx=0,
                base_bssid="00:00:00:00:00:00",
                bytes_rx=1734657616,
                bytes_tx=7776356678,
                channel_utilization=True,
                channel_utilization_percent=24,
                channel_utilization_timestamp=1724443425,
                channels=[],
                client_count=0,
                country_code=756,
                country_name="CH",
                detect_interfering=False,
                detected_rogue_aps=0,
                detected_rogue_infra_aps=0,
                health=AccessPointHealth(general=None, channel_utilization=HealthMetric(value=24, severity="good"), client_count=HealthMetric(value=0, severity="good"), interfering_ssids=HealthMetric(value=0, severity="good"), infra_interfering_ssids=HealthMetric(value=0, severity="good"), overall=HealthMetric(value=0, severity="good")),
            ),
            Radio(
                radio_id=2,
                mode="AP",
                all_ssids=True,
                auto_txpower=False,
                background_scan_enabled=False,
                bandwidth_rx=44,
                bandwidth_tx=336,
                base_bssid="00:00:00:00:00:00",
                bytes_rx=57289877156,
                bytes_tx=166974595457,
                channel_utilization=True,
                channel_utilization_percent=6,
                channel_utilization_timestamp=1724443425,
                channels=[],
                client_count=1,
                country_code=756,
                country_name="CH",
                detect_interfering=False,
                detected_rogue_aps=0,
                detected_rogue_infra_aps=0,
                health=AccessPointHealth(general=None, channel_utilization=HealthMetric(value=6, severity="good"), client_count=HealthMetric(value=1, severity="good"), interfering_ssids=HealthMetric(value=0, severity="good"), infra_interfering_ssids=HealthMetric(value=0, severity="good"), overall=HealthMetric(value=0, severity="good")),
            ),
            Radio(
                radio_id=3,
                mode="Monitor",
                all_ssids=None,
                auto_txpower=None,
                background_scan_enabled=None,
                bandwidth_rx=None,
                bandwidth_tx=None,
                base_bssid=None,
                bytes_rx=None,
                bytes_tx=None,
                channel_utilization=None,
                channel_utilization_percent=None,
                channel_utilization_timestamp=None,
                channels=None,
                client_count=None,
                country_code=None,
                country_name=None,
                detect_interfering=None,
                detected_rogue_aps=69,
                detected_rogue_infra_aps=64,
                health=AccessPointHealth(general=None, channel_utilization=HealthMetric(value=0, severity="good"), client_count=HealthMetric(value=0, severity="good"), interfering_ssids=HealthMetric(value=0, severity="good"), infra_interfering_ssids=HealthMetric(value=0, severity="good"), overall=HealthMetric(value=0, severity="good")),
            ),
            Radio(radio_id=4, mode="Virtual Lan AP", all_ssids=None, auto_txpower=None, background_scan_enabled=None, bandwidth_rx=None, bandwidth_tx=None, base_bssid=None, bytes_rx=None, bytes_tx=None, channel_utilization=None, channel_utilization_percent=None, channel_utilization_timestamp=None, channels=None, client_count=None, country_code=None, country_name=None, detect_interfering=None, detected_rogue_aps=None, detected_rogue_infra_aps=None, health=None),
            Radio(radio_id=5, mode="Not Exist", all_ssids=None, auto_txpower=None, background_scan_enabled=None, bandwidth_rx=None, bandwidth_tx=None, base_bssid=None, bytes_rx=None, bytes_tx=None, channel_utilization=None, channel_utilization_percent=None, channel_utilization_timestamp=None, channels=None, client_count=None, country_code=None, country_name=None, detect_interfering=None, detected_rogue_aps=None, detected_rogue_infra_aps=None, health=None),
        ],
        eos=False,
        wired=[
            WiredInterface(interface="lan1", bytes_rx=245200771025, bytes_tx=160819904621, packets_rx=300058497, packets_tx=265495953, errors_rx=0, errors_tx=0, dropped_rx=5081872, dropped_tx=0, collisions=0, link_speed_mbps=1000, is_carrier_link=True, is_full_duplex=True, max_link_speed=1000),
            WiredInterface(interface="lan2", bytes_rx=0, bytes_tx=0, packets_rx=0, packets_tx=0, errors_rx=0, errors_tx=0, dropped_rx=0, dropped_tx=0, collisions=0, link_speed_mbps=0, is_carrier_link=False, is_full_duplex=False, max_link_speed=1000),
        ],
        health=AccessPointHealth(general=GeneralHealth(country_code=HealthMetric(value=0, severity="good"), uplink_status=[HealthMetric(value=1000, severity="good"), HealthMetric(value=0, severity="good")], overall=HealthMetric(value=0, severity="good")), channel_utilization=None, client_count=None, interfering_ssids=None, infra_interfering_ssids=None, overall=None),
        cpu_usage=10,
        mem_free=562836,
        mem_total=903584,
    )
}


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"action":"","build":1639,"http_method":"GET","name":"AP-NAME","path":"wifi","results":[{"ap_profile":"Profile01","ble_profile":"","board_mac":"00:00:00:00:00:00","cli_enabled":true,"clients":1,"configured_country_code":756,"configured_country_name":"CH","connecting_from":"10.10.10.10","connecting_interface":"MGMT","connection_state":"Connected","country_code_conflict":0,"cpu_usage":10,"data_chan_sec":"clear-text","dedicated_scan_enabled":false,"eos":false,"forticare_registration_status":"registered","health":{"general":{"country_code":{"severity":"good","value":0},"overall":{"severity":"good","value":0},"uplink_status":[{"severity":"good","value":1000},{"severity":"good","value":0}]}}, "image_download_progress":0,"indoor_outdoor":2,"is_local":false,"is_wpa3_supported":true,"join_time":"07/04/24 18:05","join_time_raw":1720109136,"last_failure":"N/A","last_failure_code":0,"last_reboot_time":"04/04/23 15:28","last_reboot_time_raw":1709147540,"led_blink":false,"lldp":[{"capability":"Bridge Router ","chassis_id":"mac 00:00:00:00:00:00","ip":"10.128.1.1","local_port":"lan1","mau_operating_mode":"1000BaseTFD - Four-pair Category 5 UTP, full duplex mode","port_description":"port48","port_id":"port48","system_description":"FortiSwitch-448E-FPOE v7.2.x,build0000,000000 (GA)","system_name":"switch01","vlan":-1}],"lldp_enable":true,"local_ipv4_addr":"10.128.0.1","location":"","mem_free":562836,"mem_total":903584,"mesh_hop_count":0,"mesh_uplink":"ethernet","mesh_uplink_intf":"MGMT","mesh_uplink_intf_speed":20000.0,"mgmt_vlanid":0,"name":"AP-NAME","os_version":"FP231F-v7.0-build0134","override_profile":false,"poe_mode":"auto(auto)","poe_mode_oper":"auto","radio":[{"all_ssids":true,"auto_txpower":false,"background_scan_enabled":false,"bandwidth_rx":0,"bandwidth_tx":0,"base_bssid":"00:00:00:00:00:00","bytes_rx":1734657616,"bytes_tx":7776356678,"channel_utilization":true,"channel_utilization_percent":24,"channel_utilization_timestamp":1724443425,"channels":[],"client_count":0,"country_code":756,"country_name":"CH","detect_interfering":false,"detected_rogue_aps":0,"detected_rogue_infra_aps":0,"health":{"channel_utilization":{"severity":"good","value":24},"client_count":{"severity":"good","value":0},"infra_interfering_ssids":{"severity":"good","value":0},"interfering_ssids":{"severity":"good","value":0},"overall":{"severity":"good","value":0}},"interfering_aps":0,"mac_errors_rx":0,"mac_errors_tx":0,"max_vaps":8,"mode":"AP","noise_floor":-95,"oper_chan":6,"oper_txpower":20,"override_band":false,"override_channel":false,"override_sa":false,"override_txpower":false,"override_vaps":false,"radio_id":1,"radio_max_rate_mbps":286,"radio_max_rate_standard_mbps":286,"radio_type":"802.11ax,n,g-only","ssid":{},"ssid_mode":"tunnel","sta_locate":false,"supported_bands":["b","g","n","ax"],"tx_discard_percentage":0,"tx_retries_percent":0,"txpower":100,"wids_profile":""},{"all_ssids":true,"auto_txpower":false,"background_scan_enabled":false,"bandwidth_rx":44,"bandwidth_tx":336,"base_bssid":"00:00:00:00:00:00","bytes_rx":57289877156,"bytes_tx":166974595457,"channel_utilization":true,"channel_utilization_percent":6,"channel_utilization_timestamp":1724443425,"channels":[],"client_count":1,"country_code":756,"country_name":"CH","detect_interfering":false,"detected_rogue_aps":0,"detected_rogue_infra_aps":0,"health":{"channel_utilization":{"severity":"good","value":6},"client_count":{"severity":"good","value":1},"infra_interfering_ssids":{"severity":"good","value":0},"interfering_ssids":{"severity":"good","value":0},"overall":{"severity":"good","value":0}},"interfering_aps":0,"mac_errors_rx":0,"mac_errors_tx":0,"max_vaps":8,"mode":"AP","noise_floor":-95,"oper_chan":40,"oper_txpower":23,"override_band":false,"override_channel":false,"override_sa":false,"override_txpower":false,"override_vaps":false,"radio_id":2,"radio_max_rate_mbps":286,"radio_max_rate_standard_mbps":286,"radio_type":"802.11ax-5G","ssid":{},"ssid_mode":"tunnel","sta_locate":false,"supported_bands":["a","n-5G","ac","ax-5G"],"tx_discard_percentage":0,"tx_retries_percent":0,"txpower":100,"wids_profile":""},{"detected_rogue_aps":69,"detected_rogue_infra_aps":64,"health":{"channel_utilization":{"severity":"good","value":0},"client_count":{"severity":"good","value":0},"infra_interfering_ssids":{"severity":"good","value":0},"interfering_ssids":{"severity":"good","value":0},"overall":{"severity":"good","value":0}},"max_2g_channel":6,"max_2g_channel_utilization":46,"max_5g_channel":0,"max_5g_channel_utilization":0,"min_2g_channel":13,"min_2g_channel_utilization":3,"min_5g_channel":0,"min_5g_channel_utilization":0,"mode":"Monitor","radio_id":3,"radio_type":"unknown","supported_bands":["a","b","g","n","n-5G","ac"],"wids_profile":""},{"mode":"Virtual Lan AP","radio_id":4,"radio_type":"unknown","supported_bands":[]},{"mode":"Not Exist","radio_id":5,"radio_type":"unknown","supported_bands":[]}],"reboot_last_day":false,"region":"","region_code":"E ","sensors_temperatures":[59],"serial":"Serial01","ssid":[{"list":["Business","Guest","IoT"],"radio":1},{"list":["Business","Guest","IoT"],"radio":2}],"state":"authorized","status":"connected","subtype":0,"vdom":"root","wan_802_1x_method":"all","wan_port_auth":"none","wan_status":[{"interface":"lan1","is_carrier_link":true,"is_full_duplex":true,"link_speed_mbps":1000},{"interface":"lan2","is_carrier_link":false,"is_full_duplex":false,"link_speed_mbps":0}],"wanlan_mode":"wan-only","wired":[{"bytes_rx":245200771025,"bytes_tx":160819904621,"collisions":0,"dropped_rx":5081872,"dropped_tx":0,"errors_rx":0,"errors_tx":0,"interface":"lan1","is_carrier_link":true,"is_full_duplex":true,"link_speed_mbps":1000,"max_link_speed":1000,"packets_rx":300058497,"packets_tx":265495953},{"bytes_rx":0,"bytes_tx":0,"collisions":0,"dropped_rx":0,"dropped_tx":0,"errors_rx":0,"errors_tx":0,"interface":"lan2","is_carrier_link":false,"is_full_duplex":false,"link_speed_mbps":0,"max_link_speed":1000,"packets_rx":0,"packets_tx":0}],"wtp_id":"Serial01","wtp_mode":"normal"}],"serial":"Serial01","status":"success","vdom":"root","version":"v7.2.x"}'
                ]
            ],
            [
                AP_SECTION,
            ],
        ),
    ],
)
def test_parse_fortios_managed_ap(string_table, expected_section) -> None:
    assert parse_fortios_managed_ap(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "AP-NAME",
            [
                AP_SECTION,
            ],
            [
                Result(
                    state=State.OK,
                    summary="Status: connected, State: authorized, Clients: 1, IP: 10.128.0.1",
                    details="\n            Serial: Serial01\n            AP MAC: 00:00:00:00:00:00\n            Last reboot: 04/04/23 15:28\n            \n            Health:\n            - AP general: good\n            - Radio 1: good\n- Radio 2: good\n\n            SSIDs:\n- Radio 1: Business  Guest  IoT  \n- Radio 2: Business  Guest  IoT  \n\n            LLDP information:\n            - Local port: lan1\n                - Remote device: switch01\n                - Remote description: FortiSwitch-448E-FPOE v7.2.x,build0000,000000 (GA)\n                - Remote port: port48\n\n                \n            ",
                )
            ],
        ),
    ],
)
def test_check_fortios_managed_ap(item: str, section: str, expected_check_result: Tuple) -> None:
    with patch("cmk.base.plugins.agent_based.fortios_managed_ap.get_value_store") as mock_get:
        timestamp = int((datetime.now() - timedelta(minutes=2)).timestamp())
        mock_get.return_value = {"bytes_tx": (timestamp, 0.0), "bytes_rx": (timestamp, 0.0)}
        mock_get.return_value = {"errors_tx": (timestamp, 0.0), "errors_rx": (timestamp, 0.0)}
        mock_get.return_value = {"dropped_tx": (timestamp, 0.0), "dropped_rx": (timestamp, 0.0)}
        mock_get.return_value = {"collisions": (timestamp, 0.0)}
        mock_get.return_value = {"if_out_bps": (timestamp, 0.0), "if_in_bps": (timestamp, 0.0)}
        result = list(check_fortios_managed_ap(item, section[0]))
        for res, expected_res in zip(result, expected_check_result):
            assert res == expected_res
