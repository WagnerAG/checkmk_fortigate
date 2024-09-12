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

"""
Check_MK agent based checks to be used with agent_fortios Datasource

"""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    HostLabel,
    Metric,
    Result,
    Service,
    State,
    check_levels,
    register,
    render,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, HostLabelGenerator
from pydantic import BaseModel, validator

DISCOVERY_DEFAULT_PARAMETERS = {"features": ["fortiguard", "forticare", "appctrl", "web_filtering", "antivirus", "vdom"]}
DEFAULT_LICENSE_EXPIRES_LEVEL: Dict = {"day_levels": (45, 30)}

class ModuleInterface(BaseModel, ABC):
    type: str

    @abstractmethod
    def module_name(self) -> str:
        pass

    @abstractmethod
    def summary(self) -> str:
        pass

# FortiGuard module
class FortiGuardModule(ModuleInterface):
    type: str = "cloud_service_status"
    supported: bool
    connected: bool
    has_connected: bool
    connection_issue: bool
    last_connection_success: int
    update_server_usa: bool
    next_scheduled_update: int
    scheduled_updates_enabled: bool
    server_address: str
    fortigate_wan_ip: str

    def module_name(self) -> str:
        return "fortiguard"

    @property
    def summary(self):
        next_scheduled_update = render.timespan(self.next_scheduled_update - time.time())
        return f'Supported: {self.supported} WAN IP: {self.fortigate_wan_ip}, Scheduled Update: {self.scheduled_updates_enabled}, Next update: {next_scheduled_update}'

class SupportDetail(BaseModel):
    status: str
    support_level: str
    expires: int

class Support(BaseModel):
    hardware: Optional[SupportDetail]
    enhanced: SupportDetail

# FortiCare module
class FortiCareModule(ModuleInterface):
    type: str = "cloud_service_status"
    status: str
    registration_status: str
    registration_supported: bool
    account: str
    support: Support
    company: str
    industry: str

    def module_name(self) -> str:
        return "forticare"

    @property
    def summary(self):
        expires_enhanced = render.timespan(self.support.enhanced.expires - time.time())
        return f'Account: {self.account}, Status: {self.status}, Expires: {expires_enhanced}'

    @property
    def details(self):
        if "hardware" in self.support:
            expires_hardware = render.timespan(self.support.hardware.expires - time.time())
            status_hardware = self.support.hardware.status
        else:
            expires_hardware = "N/A"
            status_hardware = "N/A - virtual platform"
        return f'Support Enhanced: {self.support.enhanced.status} expires in: {convert_number_of_days(self.support.enhanced.expires)} days, Support Hardware: {status_hardware} expires in: {expires_hardware})'


# AppCtrl module
class AppCtrlModule(ModuleInterface):
    type: str = "downloaded_fds_object"
    status: str
    version: str
    expires: int
    entitlement: str
    last_update: int
    last_update_attempt: int
    last_update_result_status: str
    last_update_method_status: str

    def module_name(self) -> str:
        return "appctrl"

    @property
    def summary(self):
        expires = render.timespan(self.expires - time.time())
        return f"Module {self.entitlement} Version: {self.version}, Status: {self.status}, Expires: {expires}"


# Web filtering module
class WebFilteringModule(ModuleInterface):
    type: str = "live_fortiguard_service"
    status: str
    expires: int
    entitlement: str
    category_list_version: int
    running: bool

    def module_name(self) -> str:
        return "web_filtering"

    @property
    def summary(self):
        expires = render.timespan(self.expires - time.time())
        return f"Module {self.entitlement} running: {self.running}, Status: {self.status}, Expires: {expires}"


# Antivirus module
class AntivirusModule(ModuleInterface):
    type: str = "downloaded_fds_object"
    status: str
    version: str
    expires: int
    entitlement: str
    last_update: int
    last_update_attempt: int
    last_update_result_status: str
    last_update_method_status: str
    db_status: Optional[str] = None
    engine: Optional[Dict[str, Any]] = None

    def module_name(self) -> str:
        return "antivirus"

    @property
    def summary(self):
        expires = render.timespan(self.expires - time.time())
        return f"License module {self.entitlement}, Status: {self.status}, Version: {self.version}, Last update: {render.datetime(self.last_update)}, Expires in: {expires}"


class Vdom(ModuleInterface):
    type: str = "platform"
    can_upgrade: bool = False
    used: int
    max: int

    def module_name(self) -> str:
        return "vdom"

    @property
    def summary(self):
        remaining_vdoms = self.max - self.used
        return f"Maximum VDOMs: {self.max}, Remaining VDOMs: {remaining_vdoms}, Upgradable: {self.can_upgrade}, Type: {self.type}"


class LicenseStatus(BaseModel):
    results: Dict[str, ModuleInterface]
    vdom: str

    @validator("results", pre=True)
    def validate_modules(cls, v):
        validated_results = {}
        module_map = {
            "fortiguard": FortiGuardModule,
            "forticare": FortiCareModule,
            "appctrl": AppCtrlModule,
            "web_filtering": WebFilteringModule,
            "antivirus": AntivirusModule,
            "vdom": Vdom,
        }
        for key, value in v.items():
            if key in module_map:
                validated_results[key] = module_map[key](**value)
        return validated_results


def parse_fortios_license(string_table) -> Mapping[str, str] | None:
    try:
        json_data = json.loads(string_table[0][0])
    except ValueError:
        json_data = {}

    license_modules = LicenseStatus(**json_data)

    return {key: item for key, item in license_modules.results.items()}

def host_label_fortios_license(section: Mapping[str, str]) -> HostLabelGenerator:
    yield HostLabel("cmk/device_type", "firewall")
    yield HostLabel("cmk/vendor", "fortigate")


def discovery_fortios_license(params: Mapping[str, Any], section: Mapping[str, str]) -> DiscoveryResult:
    # Limit modules to implemented checks
    for item in section:
        if item in params["features"]:
            yield Service(item=item)


def convert_number_of_days(epoch_time):
    days, remainder = divmod(epoch_time - time.time(), 86400)
    return days


def check_fortios_license(item: str, params: Mapping[str, Any], section: Mapping[str, str]) -> CheckResult:
    license = section.get(item)
    day_levels = params.get("day_levels", None)

    if not license:
        yield Result(state=State.UNKNOWN, summary=item)
        return

    if item == "antivirus":
        if license.status == "licensed":
            yield Result(
                state=State.OK,
                summary=license.summary,
            )

        if str(license.expires).isdigit():
            yield from check_levels(
                value=convert_number_of_days(license.expires),
                label="Antivirus license expires in number of days",
                metric_name="antivirus_license",
                levels_lower=day_levels,
                render_func=lambda v: f"{v:.0f} days",
            )

        yield Metric("last_update", convert_number_of_days(license.last_update))
        yield Metric("expires", convert_number_of_days(license.expires), levels=day_levels)

    elif item == "web_filtering":
        if license.status == "licensed":
            yield Result(
                state=State.OK,
                summary=license.summary,
            )

        if str(license.expires).isdigit():
            yield from check_levels(
                value=convert_number_of_days(license.expires),
                label="Webfilter license expires in number of days",
                metric_name="webfilter_license",
                levels_lower=day_levels,
                render_func=lambda v: f"{v:.0f} days",
            )

        yield Metric("expires", convert_number_of_days(license.expires), levels=day_levels)

    elif item == "appctrl":
        if license.status == "licensed":
            yield Result(
                state=State.OK,
                summary=license.summary,
            )

        if str(license.expires).isdigit():
            yield from check_levels(
                value=convert_number_of_days(license.expires),
                label="Appcrtl license expires in number of days",
                metric_name="appctrl_license",
                levels_lower=day_levels,
                render_func=lambda v: f"{v:.0f} days",
            )

        yield Metric("expires", convert_number_of_days(license.expires), levels=day_levels)

    elif item == "vdom":
        yield Result(
            state=State.OK,
            summary=license.summary,
        )

    elif item == "forticare":
        if license.status == "registered" and license.support.enhanced.status == "licensed":
            yield Result(state=State.OK, summary=license.summary, details=license.details)

        if str(license.support.enhanced.expires).isdigit():
            yield from check_levels(
                value=convert_number_of_days(license.support.enhanced.expires),
                label="Forticare licenses expires in number of days",
                metric_name="forticare_license",
                levels_lower=day_levels,
                render_func=lambda v: f"{v:.0f} days",
            )
        yield Metric("expires", convert_number_of_days(license.support.enhanced.expires), levels=day_levels)

    elif item == "fortiguard":
        if license.connected is True:
            yield Result(
                state=State.OK,
                summary=license.summary,
            )
        else:
            yield Result(
                state=State.WARN,
                summary=license.summary,
            )

        yield Metric("expires", convert_number_of_days(license.next_scheduled_update), levels=day_levels)


register.agent_section(
    name="fortios_license",
    parse_function=parse_fortios_license,
    host_label_function=host_label_fortios_license,
)


register.check_plugin(
    name="fortios_license",
    service_name="License %s",
    discovery_function=discovery_fortios_license,
    discovery_ruleset_name="discovery_fortios_license",
    discovery_default_parameters=DISCOVERY_DEFAULT_PARAMETERS,
    check_ruleset_name="fortios_license",
    check_default_parameters=DEFAULT_LICENSE_EXPIRES_LEVEL,
    check_function=check_fortios_license,
)
