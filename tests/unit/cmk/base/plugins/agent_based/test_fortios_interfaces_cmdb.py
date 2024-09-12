#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import pytest
from cmk.base.plugins.agent_based.fortios_interface_cmdb import (
    InterfaceCMDB,
    parse_fortios_interfaces_cmdb,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"build":1639,"http_method":"GET","http_status":200,"matched_count":51,"name":"interface","next_idx":50,"path":"system","results":[{"ac-name":"","aggregate-type":"physical","algorithm":"L4","alias":"Interface 1","allowaccess":"ping","ap-discover":"enable","arpforward":"enable","auth-cert":"","auth-portal-addr":"","auth-type":"auto","auto-auth-extension-device":"disable","bandwidth-measure-time":0,"bfd":"global","bfd-desired-min-tx":250,"bfd-detect-mult":3,"bfd-required-min-rx":250,"broadcast-forward":"disable","captive-portal":0,"cli-conn-status":0,"client-options":[],"color":0,"dedicated-to":"none","defaultgw":"enable","description":"","detected-peer-mtu":0,"detectprotocol":"ping","detectserver":"","device-identification":"disable","device-user-identification":"enable","devindex":42,"dhcp-classless-route-addition":"disable","dhcp-client-identifier":"","dhcp-relay-agent-option":"enable","dhcp-relay-interface":"","dhcp-relay-interface-select-method":"auto","dhcp-relay-ip":"","dhcp-relay-link-selection":"0.0.0.0","dhcp-relay-request-all-server":"disable","dhcp-relay-service":"disable","dhcp-relay-type":"regular","dhcp-renew-time":0,"dhcp-snooping-server-list":[],"disc-retry-timeout":1,"disconnect-threshold":0,"distance":5,"dns-server-override":"enable","dns-server-protocol":"cleartext","drop-fragment":"disable","drop-overlapped-fragment":"disable","eap-ca-cert":"","eap-identity":"","eap-method":"","eap-password":"","eap-supplicant":"disable","eap-user-cert":"","egress-shaping-profile":"","estimated-downstream-bandwidth":0,"estimated-upstream-bandwidth":0,"explicit-ftp-proxy":"disable","explicit-web-proxy":"disable","external":"disable","fail-action-on-extender":"soft-restart","fail-alert-interfaces":[],"fail-alert-method":"link-down","fail-detect":"disable","fail-detect-option":"link-down","fortilink":"disable","fortilink-backup-link":0,"fortilink-neighbor-detect":"fortilink","fortilink-split-interface":"enable","forward-domain":0,"gwdetect":"disable","ha-priority":1,"icmp-accept-redirect":"enable","icmp-send-redirect":"enable","ident-accept":"disable","idle-timeout":0,"ike-saml-server":"","inbandwidth":0,"ingress-shaping-profile":"","ingress-spillover-threshold":0,"interface":"LAN","internal":0,"ip":"10.10.10.10 255.255.255.0","ip-managed-by-fortiipam":"disable","ipmac":"disable","ips-sniffer-mode":"disable","ipunnumbered":"0.0.0.0","macaddr":"00:00:00:00:00:00","managed-subnetwork-size":"256","management-ip":"0.0.0.0 0.0.0.0","measured-downstream-bandwidth":0,"measured-upstream-bandwidth":0,"mediatype":"none","member":[],"min-links":1,"min-links-down":"operational","mode":"static","monitor-bandwidth":"disable","mtu":1500,"mtu-override":"disable","name":"Interface 1","ndiscforward":"enable","netbios-forward":"disable","netflow-sampler":"disable","outbandwidth":0,"padt-retry-timeout":1,"password":"","ping-serv-status":0,"polling-interval":20,"pppoe-unnumbered-negotiate":"enable","pptp-auth-type":"auto","pptp-client":"disable","pptp-password":"","pptp-server-ip":"0.0.0.0","pptp-timeout":0,"pptp-user":"","preserve-session-route":"disable","priority":1,"priority-override":"enable","proxy-captive-portal":"disable","q_origin_key":"Interface 1","reachable-time":30000,"remote-ip":"0.0.0.0 0.0.0.0","replacemsg-override-group":"","role":"undefined","sample-direction":"both","sample-rate":2000,"secondary-IP":"disable","secondaryip":[],"security-8021x-dynamic-vlan-id":0,"security-8021x-master":"","security-8021x-mode":"default","security-exempt-list":"","security-external-logout":"","security-external-web":"","security-groups":[],"security-mac-auth-bypass":"disable","security-mode":"none","security-redirect-url":"","service-name":"","sflow-sampler":"disable","snmp-index":33,"speed":"auto","spillover-threshold":0,"src-check":"enable","status":"up","stp":"disable","stp-ha-secondary":"priority-adjust","stpforward":"disable","stpforward-mode":"rpl-all-ext-id","subst":"disable","substitute-dst-mac":"00:00:00:00:00:00","swc-first-create":0,"swc-vlan":0,"switch-controller-access-vlan":"disable","switch-controller-arp-inspection":"disable","switch-controller-dhcp-snooping":"disable","switch-controller-dhcp-snooping-option82":"disable","switch-controller-dhcp-snooping-verify-mac":"disable","switch-controller-dynamic":"","switch-controller-feature":"none","switch-controller-igmp-snooping":"disable","switch-controller-igmp-snooping-fast-leave":"disable","switch-controller-igmp-snooping-proxy":"disable","switch-controller-iot-scanning":"disable","switch-controller-learning-limit":0,"switch-controller-mgmt-vlan":4094,"switch-controller-nac":"","switch-controller-netflow-collect":"disable","switch-controller-rspan-mode":"disable","switch-controller-source-ip":"outbound","switch-controller-traffic-policy":"","system-id":"00:00:00:00:00:00","system-id-type":"auto","tagging":[],"tcp-mss":0,"trunk":"disable","trust-ip-1":"0.0.0.0 0.0.0.0","trust-ip-2":"0.0.0.0 0.0.0.0","trust-ip-3":"0.0.0.0 0.0.0.0","trust-ip6-1":"::/0","trust-ip6-2":"::/0","trust-ip6-3":"::/0","type":"vlan","username":"","vdom":"root","vindex":0,"vlan-protocol":"8021q","vlanforward":"disable","vlanid":90,"vrf":0,"vrrp":[],"vrrp-virtual-mac":"disable","wccp":"disable","weight":0,"wins-ip":"0.0.0.0"}],"revision":"1234","serial":"Serial01","size":51,"status":"success","vdom":"root","version":"v7.0.12"}'
                ]
            ],
            {
                "Interface 1": InterfaceCMDB(
                    algorithm="L4",
                    alias="Interface 1",
                    allowaccess="ping",
                    arpforward="enable",
                    bfd="global",
                    defaultgw="enable",
                    description="",
                    detectprotocol="ping",
                    detectserver="",
                    devindex=42,
                    distance=5,
                    external="disable",
                    gwdetect="disable",
                    inbandwidth=0,
                    interface="LAN",
                    internal=0,
                    ip="10.10.10.10 255.255.255.0",
                    ipmac="disable",
                    ipunnumbered="0.0.0.0",
                    macaddr="00:00:00:00:00:00",
                    mode="static",
                    mtu=1500,
                    name="Interface 1",
                    ndiscforward="enable",
                    outbandwidth=0,
                    password="",
                    priority=1,
                    q_origin_key="Interface 1",
                    role="undefined",
                    speed="auto",
                    status="up",
                    stp="disable",
                    stpforward="disable",
                    subst="disable",
                    tagging=[],
                    trunk="disable",
                    type="vlan",
                    username="",
                    vdom="root",
                    vindex=0,
                    vlanforward="disable",
                    vlanid=90,
                    vrf=0,
                    wccp="disable",
                    weight=0,
                ),
            },
        ),
    ],
)
def test_parse_fortios_interfaces_cmdb(string_table, expected_section) -> None:
    assert parse_fortios_interfaces_cmdb(string_table) == expected_section
