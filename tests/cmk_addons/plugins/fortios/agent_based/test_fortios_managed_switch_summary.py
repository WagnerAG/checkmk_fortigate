from types import SimpleNamespace

import pytest

from cmk.agent_based.v2 import Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_managed_switch_summary import (
    check_fortios_switch_summary,
    discovery_fortios_switch_summary,
)


def _entry(rating, value=0):
    return SimpleNamespace(rating=rating, value=value)


def _section(summary):
    return SimpleNamespace(summary=summary)


def test_discovery_fortios_switch_summary():
    assert list(discovery_fortios_switch_summary(_section(SimpleNamespace(overall="good")))) == [Service()]
    assert list(discovery_fortios_switch_summary(_section(None))) == []
    assert list(discovery_fortios_switch_summary(None)) == []


def test_check_fortios_switch_summary_reports_component_states():
    summary = SimpleNamespace(
        cpu=_entry("good", 15),
        memory=_entry("warning", 80),
        temperature=None,
        poe=None,
        fan={
            "fan1": SimpleNamespace(
                rating="failed",
                fan_speed=SimpleNamespace(value=1200, unit="rpm"),
            )
        },
        psu={"psu1": _entry("good")},
        overall="warning",
    )

    results = list(check_fortios_switch_summary(_section(summary)))

    assert results == [
        Result(state=State.OK, notice="CPU: good (value: 15)"),
        Result(state=State.WARN, notice="Memory: warning (value: 80)"),
        Result(state=State.CRIT, notice="Fan fan1: failed, speed: 1200rpm"),
        Result(state=State.OK, notice="PSU psu1: good"),
        Result(state=State.CRIT, summary="Overall: warning"),
    ]


@pytest.mark.parametrize(
    "rating, expected_state",
    [("good", State.OK), ("warning", State.WARN), ("unknown", State.CRIT)],
)
def test_check_fortios_switch_summary_rating_mapping(rating, expected_state):
    results = list(
        check_fortios_switch_summary(
            _section(
                SimpleNamespace(
                    cpu=_entry(rating), memory=None, temperature=None, poe=None, fan={}, psu={}, overall=rating
                )
            )
        )
    )

    assert results[-1] == Result(state=expected_state, summary=f"Overall: {rating}")


def test_check_fortios_switch_summary_without_summary():
    assert list(check_fortios_switch_summary(None)) == []
    assert list(check_fortios_switch_summary(_section(None))) == []