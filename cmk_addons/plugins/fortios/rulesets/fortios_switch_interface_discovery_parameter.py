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

from cmk.rulesets.v1 import Title, Help, Label
from cmk.rulesets.v1.form_specs import DictElement, Dictionary, BooleanChoice, List, String, validators
from cmk.rulesets.v1.rule_specs import DiscoveryParameters, Topic


def _form_check_fortios_switch_interface_discovery() -> Dictionary:
    return Dictionary(
        title=Title("FortiOS switch interface discovery"),
        elements={
            "item_included": DictElement(
                parameter_form=List[str](
                    title=Title("Include switch ports with these descriptions in monitoring"),
                    help_text=Help("Switch ports with these descriptions will be discovered and being monitored. Can be full or partial strings, case-sensitive."),
                    element_template=String(
                        custom_validate=(validators.LengthInRange(min_value=1),),
                    ),
                    editable_order=False,
                ),
            ),
            "item_with_matching_description": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Only discover interfaces with a description matching the include list"),
                    help_text=Help("If enabled, only interfaces with a description matching the include list will be discovered."),
                    label=Label("Enable"),
                ),
            ),
            "item_excluded": DictElement(
                parameter_form=List[str](
                    title=Title("Exclude switch ports with these descriptions from monitoring"),
                    help_text=Help("Switch ports with these descriptions will not be discovered. Can be full or partial strings, case-sensitive."),
                    element_template=String(
                        custom_validate=(validators.LengthInRange(min_value=1),),
                    ),
                    editable_order=False,
                ),
            ),
            "item_with_description": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Only discover interfaces with a description"),
                    help_text=Help("If enabled, only interfaces with a description will be discovered. Exclude list still apply."),
                    label=Label("Enable"),
                ),
            ),
        },
    )


rule_spec_fortios_switch_interface_discovery = DiscoveryParameters(
    title=Title("FortiOS switch interface discovery"),
    topic=Topic.NETWORKING,
    name="fortios_switch_interface_discovery",
    parameter_form=_form_check_fortios_switch_interface_discovery,
)
