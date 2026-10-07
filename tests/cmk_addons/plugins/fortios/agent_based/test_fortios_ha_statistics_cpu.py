import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics import HANodeStats, HAStatistics
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics_cpu import (
    check_fortios_ha_statistics_cpu,
    discovery_fortios_ha_statistics_cpu,
)


@pytest.fixture
def section():
    return HAStatistics(nodes=[HANodeStats(hostname="fw01", cpu_usage=42.0)])


def test_discovery_fortios_ha_statistics_cpu(section):
    assert list(discovery_fortios_ha_statistics_cpu(section)) == [Service(item="fw01")]


@pytest.mark.parametrize(
    "cpu_usage, expected_state",
    [(42.0, State.OK), (85.0, State.WARN), (95.0, State.CRIT)],
)
def test_check_fortios_ha_statistics_cpu(section, cpu_usage, expected_state):
    section.nodes[0].cpu_usage = cpu_usage

    results = list(check_fortios_ha_statistics_cpu("fw01", {"util": (80.0, 90.0)}, section))

    assert results[0] == Metric("util", cpu_usage, levels=(80.0, 90.0), boundaries=(0, 100))
    assert any(isinstance(result, Result) and result.state == expected_state for result in results)


def test_check_fortios_ha_statistics_cpu_missing_node(section):
    assert list(check_fortios_ha_statistics_cpu("missing", {"util": (80.0, 90.0)}, section)) == [
        Result(state=State.UNKNOWN, summary="No data available for this node")
    ]