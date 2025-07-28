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
    Levels,
    RulespecGroupCheckParametersNetworking,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, TextInput, Transform

def _resources_session_params():
    return Transform(
        Dictionary(
            elements=[
                (
                    "levels",
                    Levels(
                        help=_("Thresholds for session count"),
                        default_difference=(2.0, 4.0),
                        default_levels=(5.0, 10.0),
                    ),
                )
            ],
            optional_keys=False,
        ),
        forth=lambda params: params if isinstance(params, dict) else {"levels": params},
    )


def _valuespec_fortios_resources_sessions() -> Dictionary:
    return Dictionary(
        elements=[
            ("session_levels", _resources_session_params()),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortios_resources_sessions",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("FortiOS session count levels")),
        parameter_valuespec=_valuespec_fortios_resources_sessions,
        title=lambda: _("FortiOS session count levels"),
    )
)
