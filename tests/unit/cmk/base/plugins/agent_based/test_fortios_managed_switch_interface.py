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
from typing import Dict, Tuple
from unittest.mock import patch

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_managed_switch_interface import (
    IgmpSnoopingGroup,
    PhysicalPort,
    check_fortios_switch_interface,
    parse_fortios_switch_interface,
)

DEFAULT_PARAMETERS: Dict = {}


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"switch_port_stats":{"ports":{"internal":{"collisions":0,"crc-alignments":0,"fragments":0,"jabbers":0,"l3packets":0,"rx-bcast":246,"rx-bytes":8022580264,"rx-drops":1,"rx-errors":0,"rx-mcast":4556338,"rx-oversize":0,"rx-packets":20146015,"rx-ucast":15589431,"tx-bcast":69,"tx-bytes":2466784145,"tx-drops":0,"tx-errors":0,"tx-mcast":835246,"tx-oversize":0,"tx-packets":15996955,"tx-ucast":15161640,"undersize":0},"port1":{"collisions":0,"crc-alignments":0,"fragments":0,"jabbers":0,"l3packets":0,"rx-bcast":153,"rx-bytes":2274827037,"rx-drops":89,"rx-errors":0,"rx-mcast":835251,"rx-oversize":0,"rx-packets":15997044,"rx-ucast":15161640,"tx-bcast":245,"tx-bytes":7876205654,"tx-drops":0,"tx-errors":0,"tx-mcast":4556338,"tx-oversize":0,"tx-packets":20146014,"tx-ucast":15589431,"undersize":0},"port2":{"collisions":0,"crc-alignments":0,"fragments":0,"jabbers":0,"l3packets":0,"rx-bcast":0,"rx-bytes":0,"rx-drops":0,"rx-errors":0,"rx-mcast":0,"rx-oversize":0,"rx-packets":0,"rx-ucast":0,"tx-bcast":0,"tx-bytes":0,"tx-drops":0,"tx-errors":0,"tx-mcast":0,"tx-oversize":0,"tx-packets":0,"tx-ucast":0,"undersize":0},"port3":{"collisions":0,"crc-alignments":0,"fragments":0,"jabbers":0,"l3packets":0,"rx-bcast":0,"rx-bytes":0,"rx-drops":0,"rx-errors":0,"rx-mcast":0,"rx-oversize":0,"rx-packets":0,"rx-ucast":0,"tx-bcast":0,"tx-bytes":0,"tx-drops":0,"tx-errors":0,"tx-mcast":0,"tx-oversize":0,"tx-packets":0,"tx-ucast":0,"undersize":0}},"serial":"Serial01"},"switch_ports":{"connecting_from":"10.10.10.10","dhcp_snooping_supported":true,"eos":false,"fgt_peer_intf_name":"fortilink","forticare_registration_status":"registered","igmp_snooping_supported":true,"image_download_progress":0,"is_l3":false,"join_time":"Tue Apr 2 19:08:34 2024","led_blink_supported":true,"max_poe_budget":65,"mc_lag_supported":false,"name":"Switch01","os_version":"OSVersion","ports":[{"dhcp_snooping":{"untrusted":0},"duplex":"full","fgt_peer_device_name":"Serial","fgt_peer_port_name":"internal5","fortilink_port":true,"igmp_snooping_group":{"group_count":0},"interface":"port1","isl_peer_device_name":"","isl_peer_port_name":"","isl_peer_trunk_name":"","mclag":false,"mclag_icl":false,"poe_capable":true,"poe_status":"enabled","port_power":0,"power_status":1,"speed":1000,"status":"up","supported_port_speeds":["10half","10full","100half","100full","auto","1000auto"],"vlan":"LAN"},{"dhcp_snooping":{"untrusted":0},"duplex":"half","fgt_peer_device_name":"","fgt_peer_port_name":"","fortilink_port":false,"igmp_snooping_group":{"group_count":0},"interface":"port2","isl_peer_device_name":"","isl_peer_port_name":"","isl_peer_trunk_name":"","mclag":false,"mclag_icl":false,"poe_capable":true,"poe_status":"enabled","port_power":0,"power_status":1,"speed":10,"status":"up","supported_port_speeds":["10half","10full","100half","100full","auto","1000auto"],"vlan":"LAN"},{"dhcp_snooping":{"untrusted":0},"duplex":"half","fgt_peer_device_name":"","fgt_peer_port_name":"","fortilink_port":false,"igmp_snooping_group":{"group_count":0},"interface":"port3","isl_peer_device_name":"","isl_peer_port_name":"","isl_peer_trunk_name":"","mclag":false,"mclag_icl":false,"poe_capable":true,"poe_status":"enabled","port_power":0,"power_status":1,"speed":10,"status":"up","supported_port_speeds":["10half","10full","100half","100full","auto","1000auto"],"vlan":"LAN"}],"serial":"Serial01","state":"Authorized","status":"Connected","type":"physical","vdom":"root","vlan_segment_lite_supported":true,"vlan_segment_supported":true},"switch_status":{"802-1X-settings":{"link-down-auth":"set-unauth","local-override":"disable","mab-reauth":"disable","max-reauth-attempt":3,"reauth-period":60,"tx-period":30},"access-profile":"default","custom-command":[],"delayed-restart-trigger":0,"description":"Switch","dhcp-server-access-list":"global","dhcp-snooping-static-client":[],"directly-connected":1,"dynamic-capability":"0","dynamically-discovered":1,"firmware-provision":"disable","firmware-provision-latest":"disable","firmware-provision-version":"","flow-identity":"00000000","fsw-wan1-admin":"enable","fsw-wan1-peer":"fortilink","fsw-wan2-admin":"discovered","fsw-wan2-peer":"","igmp-snooping":{"aging-time":300,"flood-unknown-multicast":"disable","local-override":"disable","vlans":[]},"ip-source-guard":[],"l3-discovered":0,"max-allowed-trunk-members":8,"mclag-igmp-snooping-aware":"enable","mirror":[],"name":"Switch01","override-snmp-community":"disable","override-snmp-sysinfo":"disable","override-snmp-trap-threshold":"disable","override-snmp-user":"disable","owner-vdom":"","poe-detection-type":1,"poe-pre-standard-detection":"disable","ports":[{"access-mode":"static","aggregator-mode":"bandwidth","allowed-vlans":[{"q_origin_key":"quarantine","vlan-name":"quarantine"}],"allowed-vlans-all":"disable","arp-inspection-trust":"untrusted","bundle":"disable","description":"","dhcp-snoop-option82-trust":"disable","dhcp-snooping":"untrusted","discard-mode":"none","dsl-profile":"","edge-port":"enable","export-to":"root","export-to-pool":"","export-to-pool-flag":0,"fec-capable":0,"fec-state":"cl91","fgt-peer-device-name":"Serial","fgt-peer-port-name":"internal5","fiber-port":0,"flags":3,"flap-duration":30,"flap-rate":5,"flap-timeout":0,"flapguard":"disable","flow-control":"disable","fortilink-port":1,"igmp-snooping-flood-reports":"disable","interface-tags":[],"ip-source-guard":"disable","isl-local-trunk-name":"","isl-peer-device-name":"","isl-peer-port-name":"","lacp-speed":"slow","learning-limit":0,"lldp-profile":"default-auto-isl","lldp-status":"tx-rx","loop-guard":"disabled","loop-guard-timeout":45,"mac-addr":"00:00:00:00:00:00","matched-dpp-intf-tags":"","matched-dpp-policy":"","max-bundle":24,"mcast-snooping-flood-traffic":"disable","mclag":"disable","mclag-icl-port":0,"media-type":"RJ45","member-withdrawal-behavior":"block","members":[],"min-bundle":1,"mode":"static","p2p-port":0,"packet-sample-rate":512,"packet-sampler":"disabled","pause-meter":0,"pause-meter-resume":"50%","poe-capable":1,"poe-max-power":"30.0W","poe-mode-bt-cabable":0,"poe-port-mode":"ieee802-3at","poe-port-power":"normal","poe-port-priority":"low-priority","poe-pre-standard-detection":"disable","poe-standard":"802.3af/at","poe-status":"enable","port-name":"port1","port-number":0,"port-owner":"","port-policy":"","port-prefix-type":0,"port-security-policy":"","port-selection-criteria":"src-dst-ip","ptp-policy":"default","q_origin_key":"port1","qos-policy":"default","rpvst-port":"disabled","sample-direction":"both","sflow-counter-interval":0,"speed":"auto","speed-mask":207,"stacking-port":0,"status":"up","sticky-mac":"disable","storm-control-policy":"default","stp-bpdu-guard":"disabled","stp-bpdu-guard-timeout":5,"stp-root-guard":"disabled","stp-state":"enabled","switch-id":"Serial01","trunk-member":0,"type":"physical","untagged-vlans":[{"q_origin_key":"quarantine","vlan-name":"quarantine"}],"virtual-port":0,"vlan":"LAN"},{"access-mode":"static","aggregator-mode":"bandwidth","allowed-vlans":[{"q_origin_key":"quarantine","vlan-name":"quarantine"}],"allowed-vlans-all":"disable","arp-inspection-trust":"untrusted","bundle":"disable","description":"","dhcp-snoop-option82-trust":"disable","dhcp-snooping":"untrusted","discard-mode":"none","dsl-profile":"","edge-port":"enable","export-to":"root","export-to-pool":"","export-to-pool-flag":0,"fec-capable":0,"fec-state":"cl91","fgt-peer-device-name":"","fgt-peer-port-name":"","fiber-port":0,"flags":2,"flap-duration":30,"flap-rate":5,"flap-timeout":0,"flapguard":"disable","flow-control":"disable","fortilink-port":0,"igmp-snooping-flood-reports":"disable","interface-tags":[],"ip-source-guard":"disable","isl-local-trunk-name":"","isl-peer-device-name":"","isl-peer-port-name":"","lacp-speed":"slow","learning-limit":0,"lldp-profile":"default-auto-isl","lldp-status":"tx-rx","loop-guard":"disabled","loop-guard-timeout":45,"mac-addr":"00:00:00:00:00:00","matched-dpp-intf-tags":"","matched-dpp-policy":"","max-bundle":24,"mcast-snooping-flood-traffic":"disable","mclag":"disable","mclag-icl-port":0,"media-type":"RJ45","member-withdrawal-behavior":"block","members":[],"min-bundle":1,"mode":"static","p2p-port":0,"packet-sample-rate":512,"packet-sampler":"disabled","pause-meter":0,"pause-meter-resume":"50%","poe-capable":1,"poe-max-power":"30.0W","poe-mode-bt-cabable":0,"poe-port-mode":"ieee802-3at","poe-port-power":"normal","poe-port-priority":"low-priority","poe-pre-standard-detection":"disable","poe-standard":"802.3af/at","poe-status":"enable","port-name":"port2","port-number":0,"port-owner":"","port-policy":"","port-prefix-type":0,"port-security-policy":"","port-selection-criteria":"src-dst-ip","ptp-policy":"default","q_origin_key":"port2","qos-policy":"default","rpvst-port":"disabled","sample-direction":"both","sflow-counter-interval":0,"speed":"auto","speed-mask":207,"stacking-port":0,"status":"up","sticky-mac":"disable","storm-control-policy":"default","stp-bpdu-guard":"disabled","stp-bpdu-guard-timeout":5,"stp-root-guard":"disabled","stp-state":"enabled","switch-id":"Serial01","trunk-member":0,"type":"physical","untagged-vlans":[{"q_origin_key":"quarantine","vlan-name":"quarantine"}],"virtual-port":0,"vlan":"LAN"},{"access-mode":"static","aggregator-mode":"bandwidth","allowed-vlans":[{"q_origin_key":"quarantine","vlan-name":"quarantine"}],"allowed-vlans-all":"disable","arp-inspection-trust":"untrusted","bundle":"disable","description":"","dhcp-snoop-option82-trust":"disable","dhcp-snooping":"untrusted","discard-mode":"none","dsl-profile":"","edge-port":"enable","export-to":"root","export-to-pool":"","export-to-pool-flag":0,"fec-capable":0,"fec-state":"cl91","fgt-peer-device-name":"","fgt-peer-port-name":"","fiber-port":0,"flags":2,"flap-duration":30,"flap-rate":5,"flap-timeout":0,"flapguard":"disable","flow-control":"disable","fortilink-port":0,"igmp-snooping-flood-reports":"disable","interface-tags":[],"ip-source-guard":"disable","isl-local-trunk-name":"","isl-peer-device-name":"","isl-peer-port-name":"","lacp-speed":"slow","learning-limit":0,"lldp-profile":"default-auto-isl","lldp-status":"tx-rx","loop-guard":"disabled","loop-guard-timeout":45,"mac-addr":"00:00:00:00:00:00","matched-dpp-intf-tags":"","matched-dpp-policy":"","max-bundle":24,"mcast-snooping-flood-traffic":"disable","mclag":"disable","mclag-icl-port":0,"media-type":"RJ45","member-withdrawal-behavior":"block","members":[],"min-bundle":1,"mode":"static","p2p-port":0,"packet-sample-rate":512,"packet-sampler":"disabled","pause-meter":0,"pause-meter-resume":"50%","poe-capable":1,"poe-max-power":"30.0W","poe-mode-bt-cabable":0,"poe-port-mode":"ieee802-3at","poe-port-power":"normal","poe-port-priority":"low-priority","poe-pre-standard-detection":"disable","poe-standard":"802.3af/at","poe-status":"enable","port-name":"port3","port-number":0,"port-owner":"","port-policy":"","port-prefix-type":0,"port-security-policy":"","port-selection-criteria":"src-dst-ip","ptp-policy":"default","q_origin_key":"port3","qos-policy":"default","rpvst-port":"disabled","sample-direction":"both","sflow-counter-interval":0,"speed":"auto","speed-mask":207,"stacking-port":0,"status":"up","sticky-mac":"disable","storm-control-policy":"default","stp-bpdu-guard":"disabled","stp-bpdu-guard-timeout":5,"stp-root-guard":"disabled","stp-state":"enabled","switch-id":"Serial01","trunk-member":0,"type":"physical","untagged-vlans":[{"q_origin_key":"quarantine","vlan-name":"quarantine"}],"virtual-port":0,"vlan":"LAN"}],"pre-provisioned":0,"q_origin_key":"Serial01","qos-drop-policy":"taildrop","qos-red-probability":12,"remote-log":[],"snmp-community":[],"snmp-sysinfo":{"contact-info":"","description":"","engine-id":"","location":"","status":"disable"},"snmp-trap-threshold":{"trap-high-cpu-threshold":80,"trap-log-full-threshold":90,"trap-low-memory-threshold":80},"snmp-user":[],"staged-image-version":"","static-mac":[],"storm-control":{"broadcast":"disable","local-override":"disable","rate":500,"unknown-multicast":"disable","unknown-unicast":"disable"},"stp-instance":[],"stp-settings":{"forward-time":15,"hello-time":2,"local-override":"disable","max-age":20,"max-hops":20,"name":"","pending-timer":4,"revision":0,"status":"enable"},"switch-device-tag":"","switch-dhcp_opt43_key":"","switch-id":"Serial01","switch-log":{"local-override":"disable","severity":"notification","status":"enable"},"switch-profile":"default","switch-stp-settings":{"status":"enable"},"tdr-supported":"yes","type":"physical","version":1}}'
                ]
            ],
            [
                {
                    "port1": PhysicalPort(
                        access_mode="static",
                        admin_vlan=None,
                        aggregator_mode="bandwidth",
                        allowed_vlans_all="disable",
                        arp_inspection_trust="untrusted",
                        bundle="disable",
                        description="",
                        discard_mode="none",
                        edge_port="enable",
                        export_to="root",
                        export_to_pool="",
                        export_to_pool_flag=0,
                        fec_capable=0,
                        fec_state="cl91",
                        fgt_peer_device_name="Serial",
                        fgt_peer_port_name="internal5",
                        fiber_port=0,
                        flags=3,
                        flow_control="disable",
                        fortilink_port=1,
                        ip_source_guard="disable",
                        isl_local_trunk_name="",
                        isl_peer_device_name="",
                        isl_peer_port_name="",
                        lacp_speed="slow",
                        learning_limit=0,
                        lldp_profile="default-auto-isl",
                        lldp_status="tx-rx",
                        loop_guard="disabled",
                        loop_guard_timeout=45,
                        mac_addr="00:00:00:00:00:00",
                        matched_dpp_intf_tags="",
                        matched_dpp_policy="",
                        max_bundle=24,
                        mclag_icl_port=0,
                        media_type="RJ45",
                        member_withdrawal_behavior="block",
                        min_bundle=1,
                        mode="static",
                        p2p_port=0,
                        packet_sample_rate=512,
                        packet_sampler="disabled",
                        pause_meter=0,
                        pause_meter_resume="50%",
                        poe_capable=1,
                        poe_max_power="30.0W",
                        poe_pre_standard_detection="disable",
                        poe_standard="802.3af/at",
                        poe_status="enable",
                        poe_=None,
                        port_name="port1",
                        port_number=0,
                        port_owner="",
                        port_policy="",
                        port_prefix_type=0,
                        port_security_policy="",
                        port_selection_criteria="src-dst-ip",
                        ptp_policy="default",
                        q_origin_key="port1",
                        qos_policy="default",
                        rpvst_port="disabled",
                        sample_direction="both",
                        sflow_counter_interval=0,
                        speed="1000",
                        speed_mask=207,
                        stacking_port=0,
                        status="up",
                        sticky_mac="disable",
                        storm_control_policy="default",
                        stp_bpdu_guard="disabled",
                        stp_bpdu_guard_timeout=5,
                        stp_root_guard="disabled",
                        stp_state="enabled",
                        switch_id="Serial01",
                        trunk_member=0,
                        type="physical",
                        virtual_port=0,
                        vlan="LAN",
                        collisions=0,
                        crc_alignments=0,
                        fragments=0,
                        jabbers=0,
                        l3packets=0,
                        rx_bcast=153,
                        rx_bytes=2274827037,
                        rx_drops=89,
                        rx_errors=0,
                        rx_mcast=835251,
                        rx_oversize=0,
                        rx_packets=15997044,
                        rx_ucast=15161640,
                        tx_bcast=245,
                        tx_bytes=7876205654,
                        tx_drops=0,
                        tx_errors=0,
                        tx_mcast=4556338,
                        tx_oversize=0,
                        tx_packets=20146014,
                        tx_ucast=15589431,
                        undersize=0,
                        duplex="full",
                        port_status="up",
                        igmp_snooping_group=IgmpSnoopingGroup(group_count=0),
                        interface="port1",
                        isl_peer_trunk_name="",
                        mclag_icl=False,
                        port_power=0.0,
                        power_status=1,
                        stp_status=None,
                        transceiver=None,
                    ),
                    "port2": PhysicalPort(
                        access_mode="static",
                        admin_vlan=None,
                        aggregator_mode="bandwidth",
                        allowed_vlans_all="disable",
                        arp_inspection_trust="untrusted",
                        bundle="disable",
                        description="",
                        discard_mode="none",
                        edge_port="enable",
                        export_to="root",
                        export_to_pool="",
                        export_to_pool_flag=0,
                        fec_capable=0,
                        fec_state="cl91",
                        fgt_peer_device_name="",
                        fgt_peer_port_name="",
                        fiber_port=0,
                        flags=2,
                        flow_control="disable",
                        fortilink_port=0,
                        ip_source_guard="disable",
                        isl_local_trunk_name="",
                        isl_peer_device_name="",
                        isl_peer_port_name="",
                        lacp_speed="slow",
                        learning_limit=0,
                        lldp_profile="default-auto-isl",
                        lldp_status="tx-rx",
                        loop_guard="disabled",
                        loop_guard_timeout=45,
                        mac_addr="00:00:00:00:00:00",
                        matched_dpp_intf_tags="",
                        matched_dpp_policy="",
                        max_bundle=24,
                        mclag_icl_port=0,
                        media_type="RJ45",
                        member_withdrawal_behavior="block",
                        min_bundle=1,
                        mode="static",
                        p2p_port=0,
                        packet_sample_rate=512,
                        packet_sampler="disabled",
                        pause_meter=0,
                        pause_meter_resume="50%",
                        poe_capable=1,
                        poe_max_power="30.0W",
                        poe_pre_standard_detection="disable",
                        poe_standard="802.3af/at",
                        poe_status="enable",
                        poe_=None,
                        port_name="port2",
                        port_number=0,
                        port_owner="",
                        port_policy="",
                        port_prefix_type=0,
                        port_security_policy="",
                        port_selection_criteria="src-dst-ip",
                        ptp_policy="default",
                        q_origin_key="port2",
                        qos_policy="default",
                        rpvst_port="disabled",
                        sample_direction="both",
                        sflow_counter_interval=0,
                        speed="10",
                        speed_mask=207,
                        stacking_port=0,
                        status="up",
                        sticky_mac="disable",
                        storm_control_policy="default",
                        stp_bpdu_guard="disabled",
                        stp_bpdu_guard_timeout=5,
                        stp_root_guard="disabled",
                        stp_state="enabled",
                        switch_id="Serial01",
                        trunk_member=0,
                        type="physical",
                        virtual_port=0,
                        vlan="LAN",
                        collisions=0,
                        crc_alignments=0,
                        fragments=0,
                        jabbers=0,
                        l3packets=0,
                        rx_bcast=0,
                        rx_bytes=0,
                        rx_drops=0,
                        rx_errors=0,
                        rx_mcast=0,
                        rx_oversize=0,
                        rx_packets=0,
                        rx_ucast=0,
                        tx_bcast=0,
                        tx_bytes=0,
                        tx_drops=0,
                        tx_errors=0,
                        tx_mcast=0,
                        tx_oversize=0,
                        tx_packets=0,
                        tx_ucast=0,
                        undersize=0,
                        duplex="half",
                        port_status="up",
                        igmp_snooping_group=IgmpSnoopingGroup(group_count=0),
                        interface="port2",
                        isl_peer_trunk_name="",
                        mclag_icl=False,
                        port_power=0.0,
                        power_status=1,
                        stp_status=None,
                        transceiver=None,
                    ),
                    "port3": PhysicalPort(
                        access_mode="static",
                        admin_vlan=None,
                        aggregator_mode="bandwidth",
                        allowed_vlans_all="disable",
                        arp_inspection_trust="untrusted",
                        bundle="disable",
                        description="",
                        discard_mode="none",
                        edge_port="enable",
                        export_to="root",
                        export_to_pool="",
                        export_to_pool_flag=0,
                        fec_capable=0,
                        fec_state="cl91",
                        fgt_peer_device_name="",
                        fgt_peer_port_name="",
                        fiber_port=0,
                        flags=2,
                        flow_control="disable",
                        fortilink_port=0,
                        ip_source_guard="disable",
                        isl_local_trunk_name="",
                        isl_peer_device_name="",
                        isl_peer_port_name="",
                        lacp_speed="slow",
                        learning_limit=0,
                        lldp_profile="default-auto-isl",
                        lldp_status="tx-rx",
                        loop_guard="disabled",
                        loop_guard_timeout=45,
                        mac_addr="00:00:00:00:00:00",
                        matched_dpp_intf_tags="",
                        matched_dpp_policy="",
                        max_bundle=24,
                        mclag_icl_port=0,
                        media_type="RJ45",
                        member_withdrawal_behavior="block",
                        min_bundle=1,
                        mode="static",
                        p2p_port=0,
                        packet_sample_rate=512,
                        packet_sampler="disabled",
                        pause_meter=0,
                        pause_meter_resume="50%",
                        poe_capable=1,
                        poe_max_power="30.0W",
                        poe_pre_standard_detection="disable",
                        poe_standard="802.3af/at",
                        poe_status="enable",
                        poe_=None,
                        port_name="port3",
                        port_number=0,
                        port_owner="",
                        port_policy="",
                        port_prefix_type=0,
                        port_security_policy="",
                        port_selection_criteria="src-dst-ip",
                        ptp_policy="default",
                        q_origin_key="port3",
                        qos_policy="default",
                        rpvst_port="disabled",
                        sample_direction="both",
                        sflow_counter_interval=0,
                        speed="10",
                        speed_mask=207,
                        stacking_port=0,
                        status="up",
                        sticky_mac="disable",
                        storm_control_policy="default",
                        stp_bpdu_guard="disabled",
                        stp_bpdu_guard_timeout=5,
                        stp_root_guard="disabled",
                        stp_state="enabled",
                        switch_id="Serial01",
                        trunk_member=0,
                        type="physical",
                        virtual_port=0,
                        vlan="LAN",
                        collisions=0,
                        crc_alignments=0,
                        fragments=0,
                        jabbers=0,
                        l3packets=0,
                        rx_bcast=0,
                        rx_bytes=0,
                        rx_drops=0,
                        rx_errors=0,
                        rx_mcast=0,
                        rx_oversize=0,
                        rx_packets=0,
                        rx_ucast=0,
                        tx_bcast=0,
                        tx_bytes=0,
                        tx_drops=0,
                        tx_errors=0,
                        tx_mcast=0,
                        tx_oversize=0,
                        tx_packets=0,
                        tx_ucast=0,
                        undersize=0,
                        duplex="half",
                        port_status="up",
                        igmp_snooping_group=IgmpSnoopingGroup(group_count=0),
                        interface="port3",
                        isl_peer_trunk_name="",
                        mclag_icl=False,
                        port_power=0.0,
                        power_status=1,
                        stp_status=None,
                        transceiver=None,
                    ),
                }
            ],
        ),
    ],
)
def test_parse_fortios_managed_switch_interface(string_table, expected_section) -> None:
    assert parse_fortios_switch_interface(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "port1",
            {
                "port1": PhysicalPort(
                    access_mode="static",
                    admin_vlan="LAN",
                    admin_poe_capable=True,
                    admin_poe_status="enable",
                    admin_speed="auto",
                    aggregator_mode="bandwidth",
                    allowed_vlans_all="disable",
                    arp_inspection_trust="untrusted",
                    bundle="disable",
                    description="Test port",
                    discard_mode="none",
                    edge_port="enable",
                    export_to="root",
                    export_to_pool="",
                    export_to_pool_flag=0,
                    fec_capable=0,
                    fec_state="cl91",
                    fgt_peer_device_name="",
                    fgt_peer_port_name="",
                    fiber_port=0,
                    flags=3,
                    flow_control="disable",
                    fortilink_port=0,
                    interface_tags=[],
                    ip_source_guard="disable",
                    isl_local_trunk_name="",
                    isl_peer_device_name="",
                    isl_peer_port_name="",
                    lacp_speed="slow",
                    learning_limit=0,
                    lldp_profile="default-auto-isl",
                    lldp_status="tx-rx",
                    loop_guard="disabled",
                    loop_guard_timeout=45,
                    mac_addr="00:00:00:00:00:00",
                    matched_dpp_intf_tags="",
                    matched_dpp_policy="",
                    max_bundle=24,
                    mclag_icl_port=0,
                    media_type="RJ45",
                    member_withdrawal_behavior="block",
                    members=[],
                    min_bundle=1,
                    mode="static",
                    p2p_port=0,
                    packet_sample_rate=512,
                    packet_sampler="disabled",
                    pause_meter=0,
                    pause_meter_resume="50%",
                    poe_capable=1,
                    poe_max_power="30.0W",
                    poe_pre_standard_detection="disable",
                    poe_standard="802.3af/at",
                    poe_status="enabled",
                    poe_=None,
                    port_name="port1",
                    port_number=0,
                    port_owner="",
                    port_policy="",
                    port_prefix_type=0,
                    port_security_policy="",
                    port_selection_criteria="src-dst-ip",
                    ptp_policy="default",
                    q_origin_key="port1",
                    qos_policy="default",
                    rpvst_port="disabled",
                    sample_direction="both",
                    sflow_counter_interval=0,
                    speed="10",
                    speed_mask=207,
                    stacking_port=0,
                    status="up",
                    sticky_mac="disable",
                    storm_control_policy="default",
                    stp_bpdu_guard="disabled",
                    stp_bpdu_guard_timeout=5,
                    stp_root_guard="disabled",
                    stp_state="enabled",
                    switch_id="Serial01",
                    trunk_member=0,
                    type="physical",
                    virtual_port=0,
                    vlan="LAN",
                    collisions=0,
                    crc_alignments=0,
                    fragments=0,
                    jabbers=0,
                    l3packets=0,
                    rx_bcast=0,
                    rx_bytes=0,
                    rx_drops=0,
                    rx_errors=0,
                    rx_mcast=0,
                    rx_oversize=0,
                    rx_packets=0,
                    rx_ucast=0,
                    tx_bcast=0,
                    tx_bytes=0,
                    tx_drops=0,
                    tx_errors=0,
                    tx_mcast=0,
                    tx_oversize=0,
                    tx_packets=0,
                    tx_ucast=0,
                    undersize=0,
                    duplex="half",
                    igmp_snooping_group=IgmpSnoopingGroup(group_count=0),
                    interface="port3",
                    isl_peer_trunk_name="",
                    mclag_icl=False,
                    port_power=0.0,
                    power_status=1,
                    port_status="up",
                    stp_status=None,
                    transceiver=None,
                )
            },
            [
                Result(
                    state=State.OK,
                    summary="[Test port], (up), MAC: 00:00:00:00:00:00, Media Type: RJ45, Speed: 10, Duplex: half, PoE Power: Searching",
                ),
                Result(state=State.OK, summary="In: 0.00 Bit/s"),
                Metric(name="if_in_bps", value=0, boundaries=(0, None)),
                Result(state=State.OK, summary="Out: 0.00 Bit/s"),
                Metric(name="if_out_bps", value=0, boundaries=(0, None)),
            ],
        ),
    ],
)
def test_check_fortios_managed_switch_interface(item: str, section: str, expected_check_result: Tuple) -> None:
    with patch("cmk.base.plugins.agent_based.fortios_managed_switch_interface.get_value_store") as mock_get:
        timestamp = int((datetime.now() - timedelta(minutes=2)).timestamp())
        mock_get.return_value = {"rx_bytes": (timestamp, 0), "tx_bytes": (timestamp, 0)}
        result = list(check_fortios_switch_interface(item, section))
        for res, expected_res in zip(result, expected_check_result):
            assert res == expected_res
