#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation in version 2. check_mk is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with GNU Make; see the file COPYING. If not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.

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
    Dictionary,
    ListChoice,
)


def _valuespec_fortios_license():
    return Dictionary(
        title=_("FortiOS license feature selection"),
        elements=[
            (
                "features",
                ListChoice(
                    choices=[
                        ("antivirus", _("Antivirus")),
                        ("forticare", _("Forticare")),
                        ("fortiguard", _("Fortiguard")),
                        ("appctrl", _("App Control")),
                        ("web_filtering", _("Web Filtering")),
                        ("vdom", _("VDOM")),
                    ],
                    default_value=[
                        "forticare",
                    ],
                    title=_("Collect information about:"),
                    help=_("Select the features you would like to monitor license informations."),
                ),
            ),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        name="discovery_fortios_license",
        valuespec=_valuespec_fortios_license,
    )
)
