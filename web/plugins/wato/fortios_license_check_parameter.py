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
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersNetworking,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, Integer, TextInput, Tuple


def _parameter_valuespec_fortios_license():
    return Dictionary(
        elements=[
            (
                "day_levels",
                Tuple(
                    title=_("Specify levels days left"),
                    elements=[
                        Integer(title=_("Warning at days left"), default_value=45),
                        Integer(title=_("Critical at days left"), default_value=30),
                    ],
                ),
            ),
        ]
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortios_license",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("FortiOS License check levels")),
        parameter_valuespec=_parameter_valuespec_fortios_license,
        title=lambda: _("FortiOS License monitoring"),
    )
)
