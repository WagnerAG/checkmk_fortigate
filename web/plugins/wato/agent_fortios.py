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
Check_MK WATO rule spec for FortiOS special agent

"""

from typing import Literal

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.datasource_programs import (
    RulespecGroupDatasourceProgramsHardware,
)
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)
from cmk.gui.valuespec import Alternative, Dictionary, FixedValue, Integer, NetworkPort, TextInput


def tls_verify_options() -> tuple[Literal["ssl"], Alternative]:
    return (
        "ssl",
        Alternative(
            title=_("SSL certificate checking"),
            elements=[
                FixedValue(value=False, title=_("Deactivated"), totext=""),
                FixedValue(value=True, title=_("Use hostname"), totext=""),
                TextInput(
                    title=_("Use other hostname"),
                    help=_("Use a custom name for the SSL certificate validation"),
                ),
            ],
            default_value=True,
        ),
    )


def tls_verify_flag_default_yes() -> tuple[Literal["no-cert-check"], Alternative]:
    return (
        "no-cert-check",
        Alternative(
            title=_("SSL certificate verification"),
            elements=[
                FixedValue(value=False, title=_("Verify the certificate"), totext=""),
                FixedValue(
                    value=True,
                    title=_("Ignore certificate errors (unsecure)"),
                    totext="",
                ),
            ],
            default_value=False,
        ),
    )


def tls_verify_flag_default_no() -> tuple[Literal["verify-cert"], Alternative]:
    return (
        "verify-cert",
        Alternative(
            title=_("SSL certificate verification"),
            elements=[
                FixedValue(value=True, title=_("Verify the certificate"), totext=""),
                FixedValue(
                    value=False,
                    title=_("Ignore certificate errors (unsecure)"),
                    totext="",
                ),
            ],
            default_value=False,
        ),
    )


def _valuespec_special_agents_fortios():
    return Dictionary(
        title=_("FortiOS"),
        elements=[
            (
                "api_token",
                IndividualOrStoredPassword(
                    title=_("API Token"),
                    allow_empty=False,
                    size=40,
                    help=_("Generate the API token through the user interface in Global VDOM" " (System -> Administrators > Create New > Rest API Admin)" " please consider to create a read only Admin Profile first"),
                ),
            ),
            (
                "port",
                NetworkPort(
                    title=_("Port"),
                    default_value=8443,
                    help=_("The port that is used for the api call."),
                ),
            ),
            tls_verify_options(),
            ("timeout", Integer(title=_("Timeout"), minvalue=1, default_value=10)),
        ],
        optional_keys=["timeout"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:fortios",
        valuespec=_valuespec_special_agents_fortios,
    )
)
