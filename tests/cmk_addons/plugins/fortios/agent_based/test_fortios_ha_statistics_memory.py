import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics import HANodeStats, HAStatistics
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics_memory import (
    check_fortios_ha_statistics_memory,
    discovery_fortios_ha_statistics_memory,
)


@pytest.fixture
def section():
    return HAStatistics(nodes=[HANodeStats(hostname="fw01", mem_usage=65.0)])


def test_discovery_fortios_ha_statistics_memory(section):
    assert list(discovery_fortios_ha_statistics_memory(section)) == [Service(item="fw01")]


@pytest.mark.parametrize(
    "memory_usage, expected_state",
    [(65.0, State.OK), (75.0, State.WARN), (85.0, State.CRIT)],
)
def test_check_fortios_ha_statistics_memory(section, memory_usage, expected_state):
    section.nodes[0].mem_usage = memory_usage

    results = list(
        check_fortios_ha_statistics_memory("fw01", {"levels": ("fixed", (70.0, 80.0))}, section)
    )

    assert results[0] == Metric("memory_util", memory_usage, levels=(70.0, 80.0), boundaries=(0, 100))
    assert any(isinstance(result, Result) and result.state == expected_state for result in results)


def test_check_fortios_ha_statistics_memory_missing_node(section):
    assert list(
        check_fortios_ha_statistics_memory("missing", {"levels": ("fixed", (70.0, 80.0))}, section)
    ) == [Result(state=State.UNKNOWN, summary="No data available for this node")]