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
from cmk.gui.valuespec import Dictionary, Float, TextInput, Tuple


def _resources_cpu_params():
    return Tuple(
        title=_("Thresholds for CPU usage"),
        elements=[
            Float(
                title=_("Warning at"),
                unit=_("percent"),
                default_value=80.0,
                help=_("CPU usage at which a warning state is triggered."),
            ),
            Float(
                title=_("Critical at"),
                unit=_("percent"),
                default_value=90.0,
                help=_("CPU usage in percent at which a critical state is triggered."),
            ),
        ],
    )


def _valuespec_fortios_resources_cpu() -> Dictionary:
    return Dictionary(
        elements=[
            ("cpu_levels", _resources_cpu_params()),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fortios_resources_cpu",
        group=RulespecGroupCheckParametersNetworking,
        item_spec=lambda: TextInput(title=_("FortiOS CPU usage levels")),
        parameter_valuespec=_valuespec_fortios_resources_cpu,
        title=lambda: _("FortiOS CPU usage levels"),
    )
)
