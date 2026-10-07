import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics import HANodeStats, HAStatistics
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics_sessions import (
    check_fortios_ha_statistics_sessions,
    discovery_fortios_ha_statistics_sessions,
)


@pytest.fixture
def section():
    return HAStatistics(nodes=[HANodeStats(hostname="fw01", sessions=1234)])


def test_discovery_fortios_ha_statistics_sessions(section):
    assert list(discovery_fortios_ha_statistics_sessions(section)) == [Service(item="fw01")]


@pytest.mark.parametrize(
    "sessions, expected_state",
    [(1234, State.OK), (25000, State.WARN), (35000, State.CRIT)],
)
def test_check_fortios_ha_statistics_sessions(section, sessions, expected_state):
    section.nodes[0].sessions = sessions

    results = list(
        check_fortios_ha_statistics_sessions("fw01", {"session_levels": ("fixed", (20000, 30000))}, section)
    )

    assert results[0] == Metric("active_sessions", sessions, levels=(20000, 30000))
    assert any(isinstance(result, Result) and result.state == expected_state for result in results)


def test_check_fortios_ha_statistics_sessions_missing_node(section):
    assert list(
        check_fortios_ha_statistics_sessions("missing", {"session_levels": ("fixed", (20000, 30000))}, section)
    ) == [Result(state=State.UNKNOWN, summary="No data available for this node")]