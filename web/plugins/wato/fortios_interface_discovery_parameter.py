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

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    RulespecGroupCheckParametersNetworking,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Checkbox,
    Dictionary,
    DropdownChoice,
    ListOfStrings,
)


def _vs_item_excluded(title, help_text):
    return DropdownChoice(
        title=title,
        choices=[
            ("name", _("Use name for exclusion")),
            ("descr", _("Use description for exclusion")),
            ("alias", _("Use alias for exclusion")),
        ],
        default_value="name",
        help=help_text,
    )

def _parameter_valuespec_interface() -> Dictionary:
    return Dictionary(
        title=_("FortiOS interface discovery"),
        elements=[
            (
                "fortios_interface_excluded",
                ListOfStrings(
                    title=_("List of interfaces to ignore"),
                    help=_("Interfaces they should be ignored by monitoring."),
                ),
            ),
            (
                "item_excluded_by_type",
                _vs_item_excluded(
                    _("Exclude network interface"),
                    _("This option makes checkmk discover interfaces either by description, alias or port id."),
                ),
            ),
            (
                "item_discovery_link_status",
                Checkbox(
                    title=_("Discover only interfaces with link status up"),
                    help=_("This option makes checkmk discover only active interfaces."),
                    label=_("Discover only active interfaces"),
                    default_value=False,
                ),
            ),
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        name="discovery_fortios_interfaces",
        valuespec=_parameter_valuespec_interface,
    )
)
