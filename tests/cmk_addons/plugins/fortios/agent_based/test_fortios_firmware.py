import json

import pytest

from cmk.agent_based.v2 import Metric, Result, Service, State
from cmk_addons.plugins.fortios.agent_based.fortios_firmware import (
    FirmwareImage,
    FirmwareSection,
    check_fortios_firmware,
    discover_fortios_firmware,
    _parse_json_section,
)


def _section(current, available=(), **config):
    return FirmwareSection.model_validate(
        {
            "results": {"current": current, "available": list(available)},
            "config": config,
        }
    )


def test_parse_fortios_firmware():
    payload = {
        "status": "success",
        "results": {
            "current": {"version": "v7.2.8", "build": 1639, "major": 7, "minor": 2, "patch": 8, "platform-id": "FGT60F"},
            "available": [],
        },
    }

    parsed = _parse_json_section([[json.dumps(payload)]])

    assert parsed.results.current.platform_id == "FGT60F"
    assert parsed.results.current.version_tuple == (7, 2, 8, 1639)
    assert parsed.results.current.build_str == "1639"
    assert _parse_json_section([]) is None
    assert _parse_json_section([["invalid JSON"]]).has_error


def test_firmware_image_normalizes_optional_values():
    image = FirmwareImage.model_validate({"platformId": "FGT40F", "maturity": "mature", "build": None})

    assert image.platform_id == "FGT40F"
    assert image.is_mature
    assert image.build_str == "Unknown"


def test_discover_fortios_firmware():
    assert list(discover_fortios_firmware(_section({"version": "v7.2.8"}))) == [Service()]
    assert list(discover_fortios_firmware(None)) == []


def test_check_fortios_firmware_without_data():
    assert list(check_fortios_firmware(None)) == [Result(state=State.UNKNOWN, summary="No firmware data received")]


@pytest.mark.parametrize(
    "section, expected_state",
    [
        (FirmwareSection(status="error", error="connection", message="Request failed"), State.UNKNOWN),
        (FirmwareSection(status="error", error="api", message="Invalid response"), State.WARN),
        (FirmwareSection(status="pending"), State.WARN),
    ],
)
def test_check_fortios_firmware_error_status(section, expected_state):
    assert list(check_fortios_firmware(section))[0].state == expected_state


def test_check_fortios_firmware_up_to_date():
    results = list(check_fortios_firmware(_section({"version": "v7.2.8", "build": 1639}, [])))

    assert results == [
        Result(state=State.OK, summary="System is up to date: v7.2.8", details="Current: v7.2.8 build 1639"),
        Metric("updates_available", 0),
    ]


def test_check_fortios_firmware_same_branch_update():
    section = _section(
        {"version": "v7.2.8", "major": 7, "minor": 2, "patch": 8, "build": 1639},
        [{"version": "v7.2.9", "major": 7, "minor": 2, "patch": 9, "build": 1700, "maturity": "mature"}],
    )

    results = list(check_fortios_firmware(section))

    assert results[0] == Result(
        state=State.WARN,
        summary="Updates available: 1 update(s) available",
        details="Current: v7.2.8 build 1639\nRecommended: v7.2.9 build 1700",
    )
    assert results[1:] == [Metric("updates_available", 1), Metric("mature_updates", 1)]


@pytest.mark.parametrize(
    "config, expected_state",
    [
        ({}, State.CRIT),
        ({"critical_on_branch_change": False}, State.WARN),
        ({"ok_if_unmatured_branch": True}, State.OK),
    ],
)
def test_check_fortios_firmware_branch_change(config, expected_state):
    section = _section(
        {"version": "v7.2.8", "major": 7, "minor": 2, "patch": 8, "build": 1639},
        [{"version": "v7.4.1", "major": 7, "minor": 4, "patch": 1, "build": 1800, "maturity": "beta"}],
        **config,
    )

    results = list(check_fortios_firmware(section))

    assert results[0].state == expected_state
    expected_summary = (
        "Only immature branch updates available: 1 update(s) available"
        if config.get("ok_if_unmatured_branch")
        else "Updates available (branch change): 1 update(s) available"
    )
    assert results[0].summary == expected_summary
    assert results[1] == Metric("updates_available", 1)


def test_check_fortios_firmware_skips_incompatible_images():
    section = _section(
        {"version": "v7.2.8", "major": 7, "minor": 2, "patch": 8, "platform-id": "FGT60F"},
        [
            {"version": "v7.2.9", "major": 7, "minor": 2, "patch": 9, "can_upgrade": False},
            {"version": "v7.4.1", "major": 7, "minor": 4, "patch": 1, "platform-id": "FGT40F"},
        ],
    )

    results = list(check_fortios_firmware(section))

    assert results[0].state == State.OK
    assert "skipped 2 incompatible images" in results[0].details
    assert results[1] == Metric("updates_available", 0)