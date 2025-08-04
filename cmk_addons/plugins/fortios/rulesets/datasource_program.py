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

from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    Integer,
    Password,
    String,
    migrate_to_password,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _valuespec_special_agents_fortios() -> Dictionary:
    return Dictionary(
        title=Title("FortiOS"),
        elements={
            "ipaddress": DictElement(
                parameter_form=String(
                    title=Title("IP Address"),
                ),
                required=True,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("TCP port number"),
                    help_text=Help("Port number for connection to the REST API."),
                    prefill=DefaultValue(8443),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=65535),),
                ),
                required=True,
            ),
            "token": DictElement(
                parameter_form=Password(
                    title=Title("API Token"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                    migrate=migrate_to_password,
                ),
                required=True,
            ),
            "ssl": DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title("Certificate Verification"),
                    prefill=DefaultValue("hostname"),
                    help_text=Help("Specify whether the host's certificate should be verified."),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="hostname",
                            title=Title("Use hostname for verification"),
                            parameter_form=FixedValue(value=None),
                        ),
                        CascadingSingleChoiceElement(
                            name="deactivate",
                            title=Title("Do not verify certificate"),
                            parameter_form=FixedValue(value=None),
                        ),
                    ],
                ),
                required=True,
            ),
            "retries": DictElement(
                parameter_form=Integer(
                    title=Title("Number of retries"),
                    help_text=Help("Number of retry attempts made by the special agent."),
                    prefill=DefaultValue(10),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=20),),
                ),
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Timeout for connection"),
                    help_text=Help("Number of seconds for a single connection attempt before timeout occurs."),
                    prefill=DefaultValue(10),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=20),),
                ),
            ),
            "debug": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Debug mode"),
                    label=Label("enabled"),
                ),
            ),
        },
    )


rule_spec_fortios_datasource_programs = SpecialAgent(
    name="fortios",
    title=Title("FortiOS Agent"),
    topic=Topic.NETWORKING,
    parameter_form=_valuespec_special_agents_fortios,
    help_text=("This rule selects the Agent FortiOS instead of the normal Check_MK Agent which collects the data through the Fortigate REST API"),
)
