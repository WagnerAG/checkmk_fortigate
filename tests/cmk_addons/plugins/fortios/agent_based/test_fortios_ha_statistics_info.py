import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics import HANodeStats, HAStatistics, VdomStats
from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics_info import (
    check_fortios_ha_statistics,
    discovery_fortios_ha_statistics,
)


@pytest.fixture
def section():
    return HAStatistics(
        nodes=[
            HANodeStats(
                hostname="fw01",
                serial_no="FGT123",
                net_usage=10.0,
                vir_usage=2.0,
                intr_usage=1.0,
                tbyte=1024,
                tpacket=55,
                uptime=9000,
                per_vdom_stats=[VdomStats(vdom="root", cpu_usage=20, mem_usage=30, sessions=50)],
            )
        ]
    )


def test_discovery_fortios_ha_statistics(section):
    assert list(discovery_fortios_ha_statistics(section)) == [Service(item="fw01")]


def test_check_fortios_ha_statistics(section):
    results = list(check_fortios_ha_statistics("fw01", section))

    assert results[0].state == State.OK
    assert results[0].summary.startswith("Serial: FGT123, Uptime:")
    assert "Throughput:" in results[0].summary
    assert "VDOM root: CPU 20.0%, Memory 30.0%, Sessions 50" in results[0].details
    assert results[1:] == [
        Metric("net_usage", 10.0, boundaries=(0, 100)),
        Metric("vir_usage", 2.0, boundaries=(0, 100)),
        Metric("intr_usage", 1.0, boundaries=(0, 100)),
    ]


def test_check_fortios_ha_statistics_missing_node(section):
    assert list(check_fortios_ha_statistics("missing", section)) == [
        Result(state=State.UNKNOWN, summary="No data available for this node")
    ]