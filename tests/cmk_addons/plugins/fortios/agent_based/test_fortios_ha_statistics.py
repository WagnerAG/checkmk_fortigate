import json

import pytest

from cmk_addons.plugins.fortios.agent_based.fortios_ha_statistics import (
    HANodeStats,
    HAStatistics,
    VdomStats,
    parse_fortios_ha_statistics,
)


def test_parse_fortios_ha_statistics():
    payload = {"results": [{"hostname": "fw01", "cpu_usage": 42, "per_vdom_stats": [{"vdom": "root"}]}]}

    parsed = parse_fortios_ha_statistics([[json.dumps(payload)]])

    expected_node = HANodeStats(hostname="fw01", cpu_usage=42, per_vdom_stats=[VdomStats(vdom="root")])
    assert parsed == HAStatistics(nodes=[expected_node])
    assert parsed.node("fw01") == expected_node
    assert parsed.node("missing") is None


@pytest.mark.parametrize(
    "string_table",
    [[], [["invalid"]], [[json.dumps({"results": []})]], [[json.dumps({"results": None})]]],
)
def test_parse_fortios_ha_statistics_without_nodes(string_table):
    assert parse_fortios_ha_statistics(string_table) is None