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
Check_MK WATO rule spec for FortiOS link monitors

"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import DefaultValue, DictElement, Dictionary, Float, InputHint, LevelDirection, ServiceState, SimpleLevels
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _form_check_fortios_link_monitor() -> Dictionary:
    return Dictionary(
        title=Title("FortiOS link monitors"),
        elements={
            "latency_levels": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Levels for latency"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=InputHint(value=(50.0, 100.0)),
                ),
            ),
            "jitter_levels": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Levels for jitter"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="ms"),
                    prefill_fixed_levels=InputHint(value=(10.0, 20.0)),
                ),
            ),
            "packet_loss_levels": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Levels for packet loss"),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="%"),
                    prefill_fixed_levels=InputHint(value=(1.0, 5.0)),
                ),
            ),
            "state_dead": DictElement(
                parameter_form=ServiceState(
                    title=Title("State if the link monitor is dead"),
                    help_text=Help("Monitoring state that is reported if the link monitor is not alive"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
            ),
        },
    )


rule_spec_fortios_link_monitor = CheckParameters(
    title=Title("FortiOS link monitors"),
    topic=Topic.NETWORKING,
    name="fortios_link_monitor",
    parameter_form=_form_check_fortios_link_monitor,
    condition=HostAndItemCondition(item_title=Title("Link monitor name and interface")),
)
