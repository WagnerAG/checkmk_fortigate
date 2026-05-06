#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    Integer,
    LevelDirection,
    MultipleChoice,
    MultipleChoiceElement,
    SimpleLevels,
    validators,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _form_check_fortios_certificate_expiry() -> Dictionary:
    return Dictionary(
        title=Title("FortiOS certificate check"),
        help_text=Help(
            "Configure expiry thresholds and filter which certificates are included in the check output."
        ),
        elements={
            "day_levels": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Days left until a certificate expires"),
                    level_direction=LevelDirection.UPPER,
                    custom_validate=(validators.LengthInRange(min_value=1),),
                    form_spec_template=Integer(),
                    prefill_fixed_levels=InputHint(value=(30, 7)),
                    help_text=Help(
                        "The specified values define the number of days remaining before "
                        "a certificate expires at which the validation status is set to WARN or CRIT."
                    ),
                ),
                required=True,
            ),
            "source": DictElement(
                parameter_form=MultipleChoice(
                    title=Title("Certificate sources"),
                    elements=[
                        MultipleChoiceElement(
                            name="factory",
                            title=Title("factory"),
                        ),
                        MultipleChoiceElement(
                            name="user",
                            title=Title("user"),
                        ),
                    ],
                ),
                required=True,
            ),
            "discover_ca": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Include CA certificates"),
                    label=Title("Enable checking of CA certificates"),
                    prefill=DefaultValue(True),
                ),
                required=True,
            ),
        },
    )


rule_spec_fortios_certificate_expiry = CheckParameters(
    name="fortios_certificate_expiry",
    title=Title("FortiOS certificate expiry check"),
    topic=Topic.NETWORKING,
    parameter_form=_form_check_fortios_certificate_expiry,
    condition=HostCondition(),
)