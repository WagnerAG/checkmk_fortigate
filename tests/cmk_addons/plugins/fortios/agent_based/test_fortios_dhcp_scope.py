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
from cmk.agent_based.v2 import (
    Metric,
    Result,
    State,
)

from cmk_addons.plugins.fortios.agent_based.fortios_dhcp_lease import (
    DhcpLease,
    parse_fortios_dhcp_lease,
)
from cmk_addons.plugins.fortios.agent_based.fortios_dhcp_scope import (
    DEFAULT_DHCP_LEVELS,
    DhcpServer,
    IpRange,
    check_fortios_dhcp_scope,
    parse_fortios_dhcp_scope,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"action": "", "build": 2795, "http_method": "GET", "http_status": 200, "limit_reached": false, "matched_count": 3, "name": '
                    '"server", "next_idx": 2, "path": "system.dhcp", "results": [{"auto-configuration": "enable", "auto-managed-status": "enable", '
                    '"conflicted-ip-timeout": 1800, "ddns-auth": "disable", "ddns-key": "ENC Key01", "ddns-keyname": "", "ddns-server-ip": "0.0.0.0", '
                    '"ddns-ttl": 300, "ddns-update": "disable", "ddns-update-override": "disable", "ddns-zone": "", "default-gateway": "10.10.10.1", '
                    '"dhcp-settings-from-fortiipam": "disable", "dns-server1": "0.0.0.0", "dns-server2": "0.0.0.0", "dns-server3": "0.0.0.0", '
                    '"dns-server4": "0.0.0.0", "dns-service": "specify", "domain": "", "exclude-range": [], "filename": "", "forticlient-on-net-status": '
                    '"enable", "id": 2, "interface": "fortilink", "ip-mode": "range", "ip-range": [{"end-ip": "10.10.10.254", "id": 1, "lease-time": 0, '
                    '"q_origin_key": 1, "start-ip": "10.10.10.2", "uci-match": "disable", "uci-string": [], "vci-match": "disable", "vci-string": []}], '
                    '"ipsec-lease-hold": 60, "lease-time": 604800, "mac-acl-default-action": "assign", "netmask": "255.255.255.0", "next-server": '
                    '"0.0.0.0", "ntp-server1": "0.0.0.0", "ntp-server2": "0.0.0.0", "ntp-server3": "0.0.0.0", "ntp-service": "local", "options": [], '
                    '"q_origin_key": 2, "relay-agent": "0.0.0.0", "reserved-address": [], "server-type": "regular", "shared-subnet": "disable", '
                    '"status": "enable", "tftp-server": [], "timezone": "", "timezone-option": "disable", "vci-match": "enable", "vci-string": '
                    '[{"q_origin_key": "FortiSwitch", "vci-string": "FortiSwitch"}, {"q_origin_key": "FortiExtender", "vci-string": "FortiExtender"}], '
                    '"wifi-ac-service": "specify", "wifi-ac1": "0.0.0.0", "wifi-ac2": "0.0.0.0", "wifi-ac3": "0.0.0.0", "wins-server1": "0.0.0.0", '
                    '"wins-server2": "0.0.0.0"}], "revision": "rev01", "serial": "Serial01", "size": 3, "status": "success", "vdom": "root", "version": '
                    '"v7.4.x"}'
                ]
            ],
            {
                "10.10.10.0/24": DhcpServer(
                    q_origin_key=2,
                    status="enable",
                    interface="fortilink",
                    ip_range=[
                        IpRange(
                            start_ip="10.10.10.2",
                            end_ip="10.10.10.254",
                        )
                    ],
                )
            },
        ),
    ],
)
def test_parse_fortios_dhcp_scope_new(string_table, expected_section) -> None:
    assert parse_fortios_dhcp_scope(string_table) == expected_section


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"action": "", "build": 2795, "http_method": "GET", "http_status": 200, "limit_reached": false, '
                    '"matched_count": 3, "name": "server", "next_idx": 2, "path": "system.dhcp", '
                    '"results": ['
                    '{"auto-configuration": "enable", "auto-managed-status": "enable", "conflicted-ip-timeout": 1800, '
                    '"ddns-auth": "disable", "ddns-key": "ENC xyz", "ddns-keyname": "", '
                    '"ddns-server-ip": "0.0.0.0", "ddns-ttl": 300, "ddns-update": "disable", "ddns-update-override": "disable", '
                    '"ddns-zone": "", "default-gateway": "10.10.10.1", "dhcp-settings-from-fortiipam": "disable", '
                    '"dns-server1": "0.0.0.0", "dns-server2": "0.0.0.0", "dns-server3": "0.0.0.0", "dns-server4": "0.0.0.0", '
                    '"dns-service": "specify", "domain": "", "exclude-range": [], "filename": "", '
                    '"forticlient-on-net-status": "enable", "id": 2, "interface": "fortilink", "ip-mode": "range", '
                    '"ip-range": [{"end-ip": "10.10.10.254", "id": 1, "lease-time": 0, "q_origin_key": 1, '
                    '"start-ip": "10.10.10.2", "uci-match": "disable", "uci-string": [], "vci-match": "disable", "vci-string": []}], '
                    '"ipsec-lease-hold": 60, "lease-time": 604800, "mac-acl-default-action": "assign", '
                    '"netmask": "255.255.255.0", "next-server": "0.0.0.0", "ntp-server1": "0.0.0.0", "ntp-server2": "0.0.0.0", '
                    '"ntp-server3": "0.0.0.0", "ntp-service": "local", "options": [], "q_origin_key": 2, "relay-agent": "0.0.0.0", '
                    '"reserved-address": [], "server-type": "regular", "shared-subnet": "disable", "status": "enable", '
                    '"tftp-server": [], "timezone": "", "timezone-option": "disable", '
                    '"vci-match": "enable", "vci-string": [{"q_origin_key": "FortiSwitch", "vci-string": "FortiSwitch"}, '
                    '{"q_origin_key": "FortiExtender", "vci-string": "FortiExtender"}], '
                    '"wifi-ac-service": "specify", "wifi-ac1": "0.0.0.0", "wifi-ac2": "0.0.0.0", "wifi-ac3": "0.0.0.0", '
                    '"wins-server1": "0.0.0.0", "wins-server2": "0.0.0.0"}'
                    '], "revision": "abcde", "serial": "Serial01", '
                    '"size": 3, "status": "success", "vdom": "root", "version": "v7.4.x"}'
                ]
            ],
            {
                "10.10.10.0/24": DhcpServer(
                    q_origin_key=2,
                    status="enable",
                    interface="fortilink",
                    ip_range=[
                        IpRange(
                            start_ip="10.10.10.2",
                            end_ip="10.10.10.254",
                        )
                    ],
                )
            },
        ),
    ],
)
def test_parse_fortios_dhcp_scope_f40(string_table, expected_section) -> None:
    assert parse_fortios_dhcp_scope(string_table) == expected_section


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"http_method":"GET","size":10,"matched_count":10,"next_idx":9,"revision":"211d6cdd911d84db8bf88be872c05bce","results":[{"id":3,"q_origin_key":3,"status":"enable","lease-time":604800,"mac-acl-default-action":"assign","forticlient-on-net-status":"enable","dns-service":"local","dns-server1":"0.0.0.0","dns-server2":"0.0.0.0","dns-server3":"0.0.0.0","dns-server4":"0.0.0.0","wifi-ac-service":"specify","wifi-ac1":"0.0.0.0","wifi-ac2":"0.0.0.0","wifi-ac3":"0.0.0.0","ntp-service":"local","ntp-server1":"0.0.0.0","ntp-server2":"0.0.0.0","ntp-server3":"0.0.0.0","domain":"","wins-server1":"0.0.0.0","wins-server2":"0.0.0.0","default-gateway":"10.128.1.1","next-server":"0.0.0.0","netmask":"255.255.255.0","interface":"fortilink","ip-range":[{"id":1,"q_origin_key":1,"start-ip":"10.128.1.100","end-ip":"10.128.1.254","vci-match":"disable","vci-string":[],"uci-match":"disable","uci-string":[],"lease-time":0}],"timezone-option":"disable","timezone":"00","tftp-server":[],"filename":"","options":[],"server-type":"regular","ip-mode":"range","conflicted-ip-timeout":1800,"ipsec-lease-hold":60,"auto-configuration":"enable","dhcp-settings-from-fortiipam":"disable","auto-managed-status":"enable","ddns-update":"disable","ddns-update-override":"disable","ddns-server-ip":"0.0.0.0","ddns-zone":"","ddns-auth":"disable","ddns-keyname":"","ddns-key":"ENC -1YkQCs+hHEqoYnXU1gvefH2QCrBw=","ddns-ttl":300,"vci-match":"enable","vci-string":[{"vci-string":"FortiSwitch","q_origin_key":"FortiSwitch"},{"vci-string":"FortiExtender","q_origin_key":"FortiExtender"}],"exclude-range":[],"reserved-address":[{"id":1,"q_origin_key":1,"type":"mac","ip":"10.128.1.100","mac":"aa:aa:bb:bb:cc:cc","action":"reserved","circuit-id-type":"string","circuit-id":"","remote-id-type":"string","remote-id":"","description":""},{"id":2,"q_origin_key":2,"type":"mac","ip":"10.128.1.101","mac":"aa:aa:bb:bb:dd:dd","action":"reserved","circuit-id-type":"string","circuit-id":"","remote-id-type":"string","remote-id":"","description":""},{"id":3,"q_origin_key":3,"type":"mac","ip":"10.128.1.102","mac":"aa:aa:bb:bb:ee:ee","action":"reserved","circuit-id-type":"string","circuit-id":"","remote-id-type":"string","remote-id":"","description":""}]}]}'
                ]
            ],
            [
                {
                    "10.128.1.0/24": DhcpServer(
                        q_origin_key=3,
                        status="enable",
                        interface="fortilink",
                        ip_range=[IpRange(start_ip="10.128.1.100", end_ip="10.128.1.254")],
                    ),
                }
            ],
        ),
    ],
)
def test_parse_fortios_dhcp_scope(string_table, expected_section) -> None:
    assert parse_fortios_dhcp_scope(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"http_method": "GET", "status": "success", "vdom": "root", "results": [{'
                    '"auto-configuration": "enable", "auto-managed-status": "enable", "conflicted-ip-timeout": 1800, '
                    '"ddns-auth": "disable", "ddns-key": "redacted", "ddns-keyname": "redacted", "ddns-server-ip": "0.0.0.0", '
                    '"ddns-ttl": 300, "ddns-update": "disable", "ddns-update-override": "disable", "ddns-zone": "", '
                    '"default-gateway": "10.44.77.254", "dhcp-settings-from-fortiipam": "disable", "dns-server1": "10.117.127.201", '
                    '"dns-server2": "172.16.101.10", "dns-server3": "0.0.0.0", "dns-server4": "0.0.0.0", "dns-service": "specify", '
                    '"domain": "", "exclude-range": [], "filename": "\\\\Default\\\\sources\\\\boot.wim", "forticlient-on-net-status": "enable", '
                    '"id": 27, "interface": "VLAN77_DATA_INS", "ip-mode": "range", "ip-range": [{"end-ip": "10.44.77.254", "id": 1, '
                    '"lease-time": 0, "q_origin_key": "redacted", "start-ip": "10.44.77.2", "uci-match": "disable", "uci-string": [], '
                    '"vci-match": "disable", "vci-string": []}], "ipsec-lease-hold": 60, "lease-time": 43200, "mac-acl-default-action": "assign", '
                    '"netmask": "255.255.255.0", "next-server": "10.117.127.42", "ntp-server1": "0.0.0.0", "ntp-server2": "0.0.0.0", '
                    '"ntp-server3": "0.0.0.0", "ntp-service": "local", "options": [{"code": 60, "id": 1, "ip": "", "q_origin_key": "redacted", '
                    '"type": "string", "uci-match": "disable", "uci-string": [], "value": "PXEClient", "vci-match": "disable", "vci-string": []}, '
                    '{"code": 66, "id": 2, "ip": "\\"10.117.127.42\\" ", "q_origin_key": "redacted", "type": "ip", "uci-match": "disable", '
                    '"uci-string": [], "value": "", "vci-match": "disable", "vci-string": []}], "q_origin_key": "redacted", '
                    '"relay-agent": "0.0.0.0", "reserved-address": [], "server-type": "regular", "shared-subnet": "disable", "status": "enable", '
                    '"tftp-server": [{"q_origin_key": "redacted", "tftp-server": "10.117.127.42"}], "timezone": "", "timezone-option": "disable", '
                    '"vci-match": "disable", "vci-string": [], "wifi-ac1": "0.0.0.0", "wifi-ac2": "0.0.0.0", "wifi-ac3": "0.0.0.0", '
                    '"wifi-ac-service": "specify", "wins-server1": "0.0.0.0", "wins-server2": "0.0.0.0"}]}'
                ]
            ],
            {
                "10.44.77.0/24": DhcpServer(
                    q_origin_key="redacted",
                    status="enable",
                    interface="VLAN77_DATA_INS",
                    ip_range=[
                        IpRange(
                            start_ip="10.44.77.2",
                            end_ip="10.44.77.254",
                        )
                    ],
                )
            },
        ),
    ],
)
def test_parse_fortios_dhcp_scope_pxe(string_table, expected_section) -> None:
    assert parse_fortios_dhcp_scope(string_table) == expected_section


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"http_method":"GET","results":[{"ip":"10.128.1.112","reserved":true,"mac":"aa:aa:bb:bb:ee:ee","vci":"FortiSwitch-448E-FPOE","hostname":"switch03","expire_time":1724645152,"status":"leased","interface":"fortilink","type":"ipv4","server_mkey":3,"server_ipam_enabled":false},{"ip":"10.128.1.111","reserved":true,"mac":"aa:aa:bb:bb:dd:dd","vci":"FortiSwitch-424E-FPOE","hostname":"switch02","expire_time":1724645151,"status":"leased","interface":"fortilink","type":"ipv4","server_mkey":3,"server_ipam_enabled":false},{"ip":"10.128.1.110","reserved":true,"mac":"aa:aa:bb:bb:cc:cc","vci":"FortiSwitch-424E-FPOE","hostname":"switch01","expire_time":1724645153,"status":"leased","interface":"fortilink","type":"ipv4","server_mkey":3,"server_ipam_enabled":false}],"vdom":"root","path":"system","name":"dhcp","action":"","status":"success","serial":"FG200FT123456789","version":"v7.2.8","build":1639}'
                ]
            ],
            [
                {
                    "aa:aa:bb:bb:cc:cc": DhcpLease(ip="10.128.1.110", reserved=True, mac="aa:aa:bb:bb:cc:cc", vci="FortiSwitch-424E-FPOE", hostname="switch01", expire_time=1724645153, status="leased", interface="fortilink", type="ipv4", server_mkey=3, server_ipam_enabled=False),
                    "aa:aa:bb:bb:dd:dd": DhcpLease(ip="10.128.1.111", reserved=True, mac="aa:aa:bb:bb:dd:dd", vci="FortiSwitch-424E-FPOE", hostname="switch02", expire_time=1724645151, status="leased", interface="fortilink", type="ipv4", server_mkey=3, server_ipam_enabled=False),
                    "aa:aa:bb:bb:ee:ee": DhcpLease(ip="10.128.1.112", reserved=True, mac="aa:aa:bb:bb:ee:ee", vci="FortiSwitch-448E-FPOE", hostname="switch03", expire_time=1724645152, status="leased", interface="fortilink", type="ipv4", server_mkey=3, server_ipam_enabled=False),
                },
            ],
        ),
    ],
)
def test_parse_fortios_dhcp_lease(string_table, expected_section) -> None:
    assert parse_fortios_dhcp_lease(string_table) == expected_section[0]


@pytest.mark.parametrize(
    "item, section_fortios_dhcp_scope, section_fortios_dhcp_lease, expected_check_result",
    [
        (
            "10.128.1.0/24",
            {
                "10.128.1.0/24": DhcpServer(
                    q_origin_key=3,
                    status="enable",
                    interface="fortilink",
                    ip_range=[
                        IpRange(start_ip="10.128.1.100", end_ip="10.128.1.254"),
                    ],
                ),
            },
            {
                "aa:aa:bb:bb:cc:cc": DhcpLease(ip="10.128.1.110", reserved=True, mac="aa:aa:bb:bb:cc:cc", vci="FortiSwitch-424E-FPOE", hostname="switch01", expire_time=1724645153, status="leased", interface="fortilink", type="ipv4", server_mkey=3, server_ipam_enabled=False),
                "aa:aa:bb:bb:dd:dd": DhcpLease(ip="10.128.1.111", reserved=True, mac="aa:aa:bb:bb:dd:dd", vci="FortiSwitch-424E-FPOE", hostname="switch02", expire_time=1724645151, status="leased", interface="fortilink", type="ipv4", server_mkey=3, server_ipam_enabled=False),
                "aa:aa:bb:bb:ee:ee": DhcpLease(ip="10.128.1.112", reserved=True, mac="aa:aa:bb:bb:ee:ee", vci="FortiSwitch-448E-FPOE", hostname="switch03", expire_time=1724645152, status="leased", interface="fortilink", type="ipv4", server_mkey=3, server_ipam_enabled=False),
            },
            [
                Metric("scope_usage", 3.0, boundaries=(0.0, 155.0)),
                Result(state=State.OK, summary="Scope usage: 1.94%"),
                Result(state=State.OK, summary="Status: enable, Interface: fortilink, Total IPs: 155, Leased IPs: 3, Available IPs: 152"),
            ],
        ),
    ],
)
def test_check_fortios_dhcp_scope(item: str, section_fortios_dhcp_scope: DhcpServer, section_fortios_dhcp_lease: DhcpLease, expected_check_result) -> None:
    actual_check_result = list(check_fortios_dhcp_scope(item, DEFAULT_DHCP_LEVELS, section_fortios_dhcp_scope, section_fortios_dhcp_lease))
    assert actual_check_result == expected_check_result
