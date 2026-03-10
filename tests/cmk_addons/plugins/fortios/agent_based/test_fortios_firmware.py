#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# WAGNER AG
# Developer: opensource@wagner.ch

import pytest
from cmk.agent_based.v2 import Metric, Result, Service, State

from cmk_addons.plugins.fortios.agent_based.fortios_firmware import (
    FirmwareConfig,
    FirmwareImage,
    FirmwareResults,
    FirmwareSection,
    _parse_json_section,
    check_fortios_firmware,
    discover_fortios_firmware,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [['{"status": "success", "results": {"current": {"version": "v7.2.7"}}}']],
            FirmwareSection(status="success", results=FirmwareResults(current=FirmwareImage(version="v7.2.7"))),
        ),
        ([["not-json"]], FirmwareSection(status="error", error="parse", message="JSON parse failed")),
        ([], None),
    ],
)
def test_parse_fortios_firmware(string_table: list[list[str]] | list[list], expected_section: FirmwareSection | None) -> None:
    assert _parse_json_section(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_services",
    [
        (FirmwareSection(status="success"), [Service()]),
        (None, []),
    ],
)
def test_discover_fortios_firmware(section: FirmwareSection | None, expected_services: list[Service]) -> None:
    assert list(discover_fortios_firmware(section)) == expected_services


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (None, [Result(state=State.UNKNOWN, summary="No firmware data received")]),
        (
            FirmwareSection(status="error", error="connection", message="Failed to connect to FortiGuard"),
            [Result(state=State.UNKNOWN, summary="Cannot check updates: Failed to connect to FortiGuard")],
        ),
        (
            FirmwareSection(
                status="success",
                results=FirmwareResults(
                    current=FirmwareImage(version="v7.2.7", build=1577, major=7, minor=2, patch=7, platform_id="FGT60F"),
                    available=[FirmwareImage(version="v7.2.8", build=1639, major=7, minor=2, patch=8, platform_id="FGT60F", maturity="M")],
                ),
            ),
            [
                Result(state=State.WARN, summary="Updates available: 1 update(s) available", details="Current: v7.2.7 build 1577\nRecommended: v7.2.8 build 1639"),
                Metric("updates_available", 1),
                Metric("mature_updates", 1),
            ],
        ),
        (
            FirmwareSection(
                status="success",
                config=FirmwareConfig(ok_if_unmatured_branch=True),
                results=FirmwareResults(
                    current=FirmwareImage(version="v7.2.7", build=1577, major=7, minor=2, patch=7, platform_id="FGT60F"),
                    available=[FirmwareImage(version="v7.4.0", build=1000, major=7, minor=4, patch=0, platform_id="FGT60F", maturity="F")],
                ),
            ),
            [
                Result(state=State.OK, summary="Only immature branch updates available: 1 update(s) available", details="Current: v7.2.7 build 1577\nRecommended: v7.4.0 build 1000\nBranch candidate: v7.4.0 build 1000"),
                Metric("updates_available", 1),
                Metric("mature_updates", 0),
            ],
        ),
    ],
)
def test_check_fortios_firmware(section: FirmwareSection | None, expected_check_result: list[Result | Metric]) -> None:
    assert list(check_fortios_firmware(section)) == expected_check_result
