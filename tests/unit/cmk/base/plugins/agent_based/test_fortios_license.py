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

from typing import Tuple

import pytest
from cmk.base.plugins.agent_based.agent_based_api.v1 import Metric, Result, State
from cmk.base.plugins.agent_based.fortios_license import (
    AntivirusModule,
    AppCtrlModule,
    FortiCareModule,
    FortiGuardModule,
    Support,
    SupportDetail,
    Vdom,
    WebFilteringModule,
    check_fortios_license,
    parse_fortios_license,
)
from freezegun import freeze_time

DISCOVERY_DEFAULT_PARAMETERS = {"features": ["fortiguard", "forticare", "appctrl", "web_filtering", "antivirus", "vdom"]}


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"http_method":"GET","results":{"fortiguard":{"type":"cloud_service_status","supported":true,"connected":true,"has_connected":true,"connection_issue":false,"last_connection_success":1700409405,"update_server_usa":false,"next_scheduled_update":1700410560,"scheduled_updates_enabled":true,"server_address":"173.243.142.6:443","fortigate_wan_ip":"1.1.1.1"},"forticare":{"type":"cloud_service_status","status":"registered","registration_status":"registered","registration_supported":true,"account":"test@test.com","support":{"hardware":{"status":"licensed","support_level":"Advanced HW","expires":1728691200},"enhanced":{"status":"licensed","support_level":"Premium","expires":1728691200}},"company":"LAB Company","industry":""},"antivirus":{"type":"downloaded_fds_object","status":"licensed","version":"91.08942","expires":1728691200,"entitlement":"AVDB","last_update":1700409405,"last_update_attempt":1700409405,"last_update_result_status":"update_result_success","last_update_method_status":"update_method_sched","db_status":"db_type_extended","engine":{"version":"6.00288","last_update":1684168260,"last_update_attempt":1700409405,"last_update_result_status":"update_result_no_updates","last_update_method_status":"update_method_manual"}},"ips":{"type":"downloaded_fds_object","status":"licensed","version":"26.00679","expires":1728691200,"entitlement":"NIDS","last_update":1700156718,"last_update_attempt":1700409405,"last_update_result_status":"update_result_no_updates","last_update_method_status":"update_method_sched","db_status":"db_type_normal","engine":{"version":"7.00326","last_update":1697586285,"last_update_attempt":1700409405,"last_update_result_status":"update_result_no_updates","last_update_method_status":"update_method_sched"},"configuration_script":{"version":"1.00010","last_update":1674488520,"last_update_attempt":1700409405,"last_update_result_status":"update_result_no_updates","last_update_method_status":"update_method_manual"}},"appctrl":{"type":"downloaded_fds_object","status":"licensed","version":"26.00679","expires":1728691200,"entitlement":"FMWR","last_update":1700156718,"last_update_attempt":1700409405,"last_update_result_status":"update_result_no_updates","last_update_method_status":"update_method_sched"},"web_filtering":{"type":"live_fortiguard_service","status":"licensed","expires":1728691200,"entitlement":"FURL","category_list_version":9,"running":true},"vdom":{"type":"platform","can_upgrade":false,"used":1,"max":10},"sms":{"type":"other","status":"no_license","used":0,"max":0}},"vdom":"root","path":"license","name":"status","action":"","status":"success","serial":"Serial01","version":"v7.2.5","build":1517}'
                ]
            ],
            {
                "fortiguard": FortiGuardModule(
                    type="cloud_service_status",
                    supported=True,
                    connected=True,
                    has_connected=True,
                    connection_issue=False,
                    last_connection_success=1700409405,
                    update_server_usa=False,
                    next_scheduled_update=1700410560,
                    scheduled_updates_enabled=True,
                    server_address="173.243.142.6:443",
                    fortigate_wan_ip="1.1.1.1",
                ),
                "forticare": FortiCareModule(
                    type="cloud_service_status",
                    status="registered",
                    registration_status="registered",
                    registration_supported=True,
                    account="test@test.com",
                    company="LAB Company",
                    industry="",
                    support=Support(
                        hardware=SupportDetail(status="licensed", support_level="Advanced HW", expires=1728691200),
                        enhanced=SupportDetail(status="licensed", support_level="Premium", expires=1728691200),
                    ),
                ),
                "antivirus": AntivirusModule(
                    type="downloaded_fds_object",
                    status="licensed",
                    version="91.08942",
                    expires=1728691200,
                    entitlement="AVDB",
                    last_update=1700409405,
                    last_update_attempt=1700409405,
                    last_update_result_status="update_result_success",
                    last_update_method_status="update_method_sched",
                    db_status="db_type_extended",
                    engine={"version": "6.00288", "last_update": 1684168260, "last_update_attempt": 1700409405, "last_update_result_status": "update_result_no_updates", "last_update_method_status": "update_method_manual"},
                ),
                "appctrl": AppCtrlModule(
                    type="downloaded_fds_object",
                    status="licensed",
                    version="26.00679",
                    expires=1728691200,
                    entitlement="FMWR",
                    last_update=1700156718,
                    last_update_attempt=1700409405,
                    last_update_result_status="update_result_no_updates",
                    last_update_method_status="update_method_sched",
                ),
                "web_filtering": WebFilteringModule(
                    type="live_fortiguard_service",
                    status="licensed",
                    expires=1728691200,
                    entitlement="FURL",
                    category_list_version=9,
                    running=True,
                ),
                "vdom": Vdom(
                type='platform', 
                can_upgrade=False, 
                used=1, max=10
                ),
            },
        ),
    ],
)
def test_parse_fortios_license(string_table, expected_section) -> None:
    assert parse_fortios_license(string_table) == expected_section

@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (

    [
        [
            '{"build": 2731, "http_method": "GET", "name": "status", "path": "license", '
            '"results": {"antivirus": {"db_status": "db_type_extended", '
            '"engine": {"last_update": 1731540540, "version": "7.00035"}, '
            '"entitlement": "AVDB", "expires": 1765152000, "last_update": 1738128300, '
            '"status": "licensed", "type": "downloaded_fds_object", "version": "93.00624"}, '
            '"appctrl": {"entitlement": "FMWR", "expires": 1765152000, '
            '"last_update": 1448933400, "status": "licensed", "type": "downloaded_fds_object", '
            '"version": "6.00741"}, '
            '"web_filtering": {"category_list_version": 10, "entitlement": "FURL", '
            '"expires": 1765152000, "running": true, "status": "licensed", '
            '"type": "live_fortiguard_service"}, '
            '"forticare": {"account": "test@test.com", "company": "MyCompany", "industry": "", '
            '"registration_status": "registered", "registration_supported": true, "status": "registered", '
            '"support": {"enhanced": {"expires": 1765152000, "status": "licensed", '
            '"support_level": "Premium"}, "hardware": {"expires": 1765152000, "status": '
            '"licensed", "support_level": "Advanced HW"}}, "type": "cloud_service_status"}, '
            '"fortiguard": {"connected": true, "connection_issue": false, '
            '"fortigate_wan_ip": "4.5.6.7", "has_connected": true, '
            '"last_connection_success": 1753776015, "next_scheduled_update": 1753777800, '
            '"scheduled_updates_enabled": true, "server_address": "1.2.3.4:443", '
            '"supported": true, "type": "cloud_service_status", "update_server_usa": false}, '
            '"vdom": {"can_upgrade": false, "max": 10, "type": "platform", "used": 1}}, '
            '"serial": "Serial01", "status": "success", "vdom": "root", "version": "v7.4.x"}'
        ]
    ],
    {
        "fortiguard": FortiGuardModule(
            type="cloud_service_status",
            supported=True,
            connected=True,
            has_connected=True,
            connection_issue=False,
            last_connection_success=1753776015,
            update_server_usa=False,
            next_scheduled_update=1753777800,
            scheduled_updates_enabled=True,
            server_address="1.2.3.4:443",
            fortigate_wan_ip="4.5.6.7",
        ),
        "forticare": FortiCareModule(
            type="cloud_service_status",
            status="registered",
            registration_status="registered",
            registration_supported=True,
            account="test@test.com",
            company="MyCompany",
            industry="",
            support=Support(
                hardware=SupportDetail(status="licensed", support_level="Advanced HW", expires=1765152000),
                enhanced=SupportDetail(status="licensed", support_level="Premium", expires=1765152000),
            ),
        ),
        "antivirus": AntivirusModule(
            type="downloaded_fds_object",
            status="licensed",
            version="93.00624",
            expires=1765152000,
            entitlement="AVDB",
            last_update=1738128300,
            db_status="db_type_extended",
            engine={"version": "7.00035", "last_update": 1731540540},
        ),
        "appctrl": AppCtrlModule(
            type="downloaded_fds_object",
            status="licensed",
            version="6.00741",
            expires=1765152000,
            entitlement="FMWR",
            last_update=1448933400,
        ),
        "web_filtering": WebFilteringModule(
            type="live_fortiguard_service",
            status="licensed",
            expires=1765152000,
            entitlement="FURL",
            category_list_version=10,
            running=True,
        ),
        "vdom": Vdom(
            type="platform",
            can_upgrade=False,
            used=1,
            max=10,
                ),
            },
        ),
    ],
)

def test_parse_fortios_license_74(string_table, expected_section) -> None:
    assert parse_fortios_license(string_table) == expected_section

@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"build": 2731, "http_method": "GET", "name": "status", "path": "license", '
                    '"results": {"antivirus": {"db_status": "db_type_extended", '
                    '"engine": {"last_update": 1731541140, '
                    '"last_update_attempt": 1753776973, "last_update_method_status": "update_method_manual", '
                    '"last_update_result_status": "update_result_not_authorized", "version": "7.00035"}, '
                    '"entitlement": "AVDB", "expires": 1691625600, "last_update": 1747991947, '
                    '"last_update_attempt": 1753776973, "last_update_method_status": "update_method_sched", '
                    '"last_update_result_status": "update_result_not_authorized", "status": "expired", '
                    '"type": "downloaded_fds_object", "version": "93.03342"}, '
                    '"appctrl": {"entitlement": "FMWR", "expires": 1786838400, '
                    '"last_update": 1739469611, "last_update_attempt": 1739538836, '
                    '"last_update_method_status": "update_method_sched", "last_update_result_status": '
                    '"update_result_no_updates", "status": "licensed", "type": "downloaded_fds_object", '
                    '"version": "6.00741"}, '
                    '"web_filtering": {"category_list_version": 10, "entitlement": "FURL", '
                    '"expires": 1691884800, "running": true, "status": "expired", '
                    '"type": "live_fortiguard_service"}, '
                    '"forticare": {"account": "company@company.com", "company": "MyCompany", "industry": "", '
                    '"registration_status": "registered", "registration_supported": true, "status": "registered", '
                    '"support": {"enhanced": {"expires": 1786838400, "status": "licensed", '
                    '"support_level": "Premium"}}, "type": "cloud_service_status"}, '
                    '"fortiguard": {"connected": true, "connection_issue": false, '
                    '"fortigate_wan_ip": "4.5.6.7", "has_connected": true, '
                    '"last_connection_success": 1753776973, "next_scheduled_update": 1753778760, '
                    '"scheduled_updates_enabled": true, "server_address": "1.2.3.4:443", '
                    '"supported": true, "type": "cloud_service_status", "update_server_usa": false}, '
                    '"vdom": {"can_upgrade": true, "max": 2, "type": "platform", "used": 1}}, '
                    '"serial": "Serial01", "status": "success", "vdom": "root", "version": "v7.4.x"}'
                ]
            ],
            {
                "fortiguard": FortiGuardModule(
                    type="cloud_service_status",
                    supported=True,
                    connected=True,
                    has_connected=True,
                    connection_issue=False,
                    last_connection_success=1753776973,
                    update_server_usa=False,
                    next_scheduled_update=1753778760,
                    scheduled_updates_enabled=True,
                    server_address="1.2.3.4:443",
                    fortigate_wan_ip="4.5.6.7",
                ),
                "forticare": FortiCareModule(
                    type="cloud_service_status",
                    status="registered",
                    registration_status="registered",
                    registration_supported=True,
                    account="company@company.com",
                    company="MyCompany",
                    industry="",
                    support=Support(
                        hardware=None,
                        enhanced=SupportDetail(
                            status="licensed",
                            support_level="Premium",
                            expires=1786838400,
                        ),
                    ),
                ),
                "antivirus": AntivirusModule(
                    type="downloaded_fds_object",
                    status="expired",
                    version="93.03342",
                    expires=1691625600,
                    entitlement="AVDB",
                    last_update=1747991947,
                    last_update_attempt=1753776973,
                    last_update_result_status="update_result_not_authorized",
                    last_update_method_status="update_method_sched",
                    db_status="db_type_extended",
                    engine={
                        "version": "7.00035",
                        "last_update": 1731541140,
                        "last_update_attempt": 1753776973,
                        "last_update_result_status": "update_result_not_authorized",
                        "last_update_method_status": "update_method_manual",
                    },
                ),
                "appctrl": AppCtrlModule(
                    type="downloaded_fds_object",
                    status="licensed",
                    version="6.00741",
                    expires=1786838400,
                    entitlement="FMWR",
                    last_update=1739469611,
                    last_update_attempt=1739538836,
                    last_update_result_status="update_result_no_updates",
                    last_update_method_status="update_method_sched",
                ),
                "web_filtering": WebFilteringModule(
                    type="live_fortiguard_service",
                    status="expired",
                    expires=1691884800,
                    entitlement="FURL",
                    category_list_version=10,
                    running=True,
                ),
                "vdom": Vdom(
                    type="platform",
                    can_upgrade=True,
                    used=1,
                    max=2,
                ),
            },
        ),
    ],
)
def test_parse_fortios_license_expired_modules(string_table, expected_section) -> None:
    assert parse_fortios_license(string_table) == expected_section

@freeze_time("2022-01-01 21:00:00")
@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        # Test case 1: All modules are supported and have valid licenses
        (
            DISCOVERY_DEFAULT_PARAMETERS,
            {
                "antivirus": AntivirusModule(
                    type="downloaded_fds_object",
                    status="licensed",
                    version="91.08942",
                    expires=1728691200,
                    entitlement="AVDB",
                    last_update=1700409405,
                    last_update_attempt=1700409405,
                    last_update_result_status="update_result_success",
                    last_update_method_status="update_method_sched",
                    db_status="db_type_extended",
                    engine={"version": "6.00288", "last_update": 1684168260, "last_update_attempt": 1700409405, "last_update_result_status": "update_result_no_updates", "last_update_method_status": "update_method_manual"},
                ),
            },
            (
                Result(state=State.OK, summary="License module AVDB, Status: licensed, Version: 91.08942, Last update: 2023-11-19 15:56:45, Expires in: 2 years 284 days"),
                Result(state=State.OK, summary="Antivirus license expires in number of days: 1014 days"),
                Metric("antivirus_license", 1014.0),
                Metric("last_update", 686.0),
                Metric("expires", 1014.0),
            ),
        ),
    ],
)
def test_check_fortios_license_antivirus(params: dict, section: dict, expected_check_result: Tuple) -> None:
        item = "antivirus"
        check_result = tuple(check_fortios_license(item, params, section))
        assert check_result == expected_check_result


@freeze_time("2022-01-01 21:00:00")
@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        # Test case 1: All modules are supported and have valid licenses
        (
            DISCOVERY_DEFAULT_PARAMETERS,
            {
                "fortiguard": FortiGuardModule(
                    type="cloud_service_status",
                    supported=True,
                    connected=True,
                    has_connected=True,
                    connection_issue=False,
                    last_connection_success=1700409405,
                    update_server_usa=False,
                    next_scheduled_update=1700410560,
                    scheduled_updates_enabled=True,
                    server_address="173.243.142.6:443",
                    fortigate_wan_ip="1.1.1.1",
                ),
            },
            (
                Result(state=State.OK, summary='Supported: True WAN IP: 1.1.1.1, Scheduled Update: True, Next update: 1 year 321 days'),
                Metric("expires", 686.0),
            ),
        ),
    ],
)
def test_check_fortios_license_fortiguard(params: dict, section: dict, expected_check_result: Tuple) -> None:
        item = "fortiguard"
        check_result = tuple(check_fortios_license(item, params, section))
        assert check_result == expected_check_result


@freeze_time("2022-01-01 21:00:00")
@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        # Test case 1: All modules are supported and have valid licenses
        (
            DISCOVERY_DEFAULT_PARAMETERS,
            {
                "forticare": FortiCareModule(
                    type="cloud_service_status",
                    status="registered",
                    registration_status="registered",
                    registration_supported=True,
                    account="test@test.com",
                    support={
                        "hardware": {"status": "licensed", "support_level": "Advanced HW", "expires": 1728691200},
                        "enhanced": {"status": "licensed", "support_level": "Premium", "expires": 1728691200},
                    },
                    company="LAB Company",
                    industry="",
                ),
            },
            (
                Result(state=State.OK, summary="Account: test@test.com, Status: registered, Expires: 2 years 284 days", details="Support Enhanced: licensed expires in: 1014.0 days, Support Hardware: N/A - virtual platform expires in: N/A)"),
                Result(state=State.OK, summary="Forticare licenses expires in number of days: 1014 days"),
                Metric("forticare_license", 1014.0),
                Metric("expires", 1014.0),
            ),
        ),
    ],
)
def test_check_fortios_license_forticare(params: dict, section: dict, expected_check_result: Tuple) -> None:
        item = "forticare"
        check_result = tuple(check_fortios_license(item, params, section))
        assert check_result == expected_check_result


@freeze_time("2022-01-01 21:00:00")
@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        # Test case 1: All modules are supported and have valid licenses
        (
            DISCOVERY_DEFAULT_PARAMETERS,
            {
                "vdom": Vdom(
                    type="platform",
                    can_upgrade=True,
                    used=5,
                    max=10,
                ),
            },
            (
                Result(state=State.OK, summary="Maximum VDOMs: 10, Remaining VDOMs: 5, Upgradable: True, Type: platform"),
            ),
        ),
    ],
)
def test_check_fortios_license_vdom(params: dict, section: dict, expected_check_result: Tuple) -> None:
        item = "vdom"
        check_result = tuple(check_fortios_license(item, params, section))
        assert check_result == expected_check_result



@freeze_time("2022-01-01 21:00:00")
@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        # Test case 1: All modules are supported and have valid licenses
        (
            DISCOVERY_DEFAULT_PARAMETERS,
            {
                "web_filtering": WebFilteringModule(
                    type="live_fortiguard_service",
                    status="licensed",
                    expires=1728691200,
                    entitlement="FURL",
                    category_list_version=9,
                    running=True,
                ),
            },
            (
                Result(state=State.OK, summary="Module FURL running: True, Status: licensed, Expires: 2 years 284 days"),
                Result(state=State.OK, summary="Webfilter license expires in number of days: 1014 days"),
                Metric("webfilter_license", 1014.0),
                Metric("expires", 1014.0),
            ),
        ),
    ],
)
def test_check_fortios_license_webfilter(params: dict, section: dict, expected_check_result: Tuple) -> None:
        item = "web_filtering"
        check_result = tuple(check_fortios_license(item, params, section))
        assert check_result == expected_check_result


@freeze_time("2022-01-01 21:00:00")
@pytest.mark.parametrize(
    "params, section, expected_check_result",
    [
        # Test case 1: All modules are supported and have valid licenses
        (
            DISCOVERY_DEFAULT_PARAMETERS,
            {
                "appctrl": AppCtrlModule(
                    type="downloaded_fds_object",
                    status="licensed",
                    version="26.00679",
                    expires=1728691200,
                    entitlement="FMWR",
                    last_update=1700156718,
                    last_update_attempt=1700409405,
                    last_update_result_status="update_result_no_updates",
                    last_update_method_status="update_method_sched",
                ),
            },
            (
                Result(state=State.OK, summary="Module FMWR Version: 26.00679, Status: licensed, Expires: 2 years 284 days"),
                Result(state=State.OK, summary="Appcrtl license expires in number of days: 1014 days"),
                Metric("appctrl_license", 1014.0),
                Metric("expires", 1014.0),
            ),
        ),
    ],
)
def test_check_fortios_license_appctrl(params: dict, section: dict, expected_check_result: Tuple) -> None:
        item = "appctrl"
        check_result = tuple(check_fortios_license(item, params, section))
        assert check_result == expected_check_result




