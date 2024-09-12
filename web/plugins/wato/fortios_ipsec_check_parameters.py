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
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersNetworking,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, ListOfStrings


def _parameter_valuespec_ipsecvpn() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "fortios_tunnels_ignore",
                ListOfStrings(
                    title=_("List of ipsec tunnel names to ignore"),
                    help=_("Tunnel names they should be ignored by monitoring"),
                ),
            ),
            (
                "fortios_tunnels_dst_subnet_ignore",
                ListOfStrings(
                    title=_("List of Destination Subnets to ignore"),
                    help=_("Tunnel destination subnets in format (10.10.10.0/255.255.255.0) they should be ignored by monitoring"),
                ),
            ),
        ],
        optional_keys=[],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortios_ipsec",
        group=RulespecGroupCheckParametersNetworking,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_ipsecvpn,
        title=lambda: _("FortiOS IPSec VPN Tunnels"),
    )
)
