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

# Source: https://github.com/Jacox98/checkmk-fortios-fw

"""FortiOS firmware monitoring (updates, branch changes, maturity).

This check extends the original FortiOS special agent with firmware information
from the FortiGate REST API endpoint: /api/v2/monitor/system/firmware.

The logic is adapted from the standalone 'fortigate_firmware' extension and
integrated under the FortiOS special agent output section 'fortios_firmware'.
"""

from __future__ import annotations

import itertools
import json
from typing import Optional

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    Metric,
    Result,
    Service,
    State,
)
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

UNKNOWN_HINTS = (
    "no route to host",
    "failed to connect",
    "failed to establish",
    "dns",
    "resolution",
    "refused",
    "timed out",
    "timeout",
)


class FirmwareImage(BaseModel):
    version: Optional[str] = None
    build: int | str | None = None
    major: int | str | None = None
    minor: int | str | None = None
    patch: int | str | None = None
    platform_id: Optional[str] = None
    maturity: Optional[str] = None
    can_upgrade: Optional[bool] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_keys(cls, value):
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        for key in ("platform-id", "platform_id", "platformId"):
            if normalized.get(key):
                normalized.setdefault("platform_id", str(normalized[key]))
                break
        return normalized

    @staticmethod
    def _to_int(value) -> int:
        try:
            return int(str(value))
        except (TypeError, ValueError):
            return 0

    @property
    def version_tuple(self) -> tuple[int, int, int, int]:
        return (
            self._to_int(self.major),
            self._to_int(self.minor),
            self._to_int(self.patch),
            self._to_int(self.build),
        )

    @property
    def build_str(self) -> str:
        return str(self.build) if self.build not in (None, "") else "Unknown"

    @property
    def is_mature(self) -> bool:
        return bool(self.maturity and str(self.maturity).strip().upper().startswith("M"))


class FirmwareResults(BaseModel):
    current: FirmwareImage = Field(default_factory=FirmwareImage)
    available: list[FirmwareImage] = Field(default_factory=list)

    @field_validator("current", mode="before")
    @classmethod
    def validate_current(cls, value):
        if isinstance(value, (dict, FirmwareImage)):
            return value
        return {}

    @field_validator("available", mode="before")
    @classmethod
    def validate_available(cls, value):
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, (dict, FirmwareImage))]


class FirmwareConfig(BaseModel):
    critical_on_branch_change: bool = True
    ok_if_unmatured_branch: bool = False


class FirmwareSection(BaseModel):
    status: str = "success"
    error: Optional[str] = None
    message: Optional[str] = None
    detail: Optional[str] = None
    results: FirmwareResults = Field(default_factory=FirmwareResults)
    config: FirmwareConfig = Field(default_factory=FirmwareConfig)

    @field_validator("results", mode="before")
    @classmethod
    def validate_results(cls, value):
        if isinstance(value, (dict, FirmwareResults)):
            return value
        return {}

    @field_validator("config", mode="before")
    @classmethod
    def validate_config(cls, value):
        if isinstance(value, (dict, FirmwareConfig)):
            return value
        return {}

    @property
    def has_error(self) -> bool:
        return self.status == "error" or self.error is not None


def _parse_error_section() -> FirmwareSection:
    return FirmwareSection(status="error", error="parse", message="JSON parse failed")


def _parse_json_section(string_table) -> FirmwareSection | None:
    if not string_table:
        return None

    try:
        flatlist = list(itertools.chain.from_iterable(string_table))
        json_str = " ".join(flatlist)
        return FirmwareSection.model_validate(json.loads(json_str))
    except (json.JSONDecodeError, TypeError, ValidationError, ValueError):
        return _parse_error_section()


agent_section_fortios_firmware = AgentSection(
    name="fortios_firmware",
    parse_function=_parse_json_section,
)


def discover_fortios_firmware(section):
    if section:
        yield Service()


def check_fortios_firmware(section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No firmware data received")
        return

    # Structured error payload from special agent
    if section.has_error:
        err_type = str(section.error or "").lower()
        msg = section.message or section.error or "Cannot retrieve firmware information"
        detail = section.detail

        is_unknown = err_type in ("connection", "timeout") or any(h in str(msg).lower() for h in UNKNOWN_HINTS) or (detail and any(h in str(detail).lower() for h in UNKNOWN_HINTS))
        state = State.UNKNOWN if is_unknown else State.WARN

        yield Result(state=state, summary=f"Cannot check updates: {msg}", details=(detail or None))
        return

    if section.status != "success":
        yield Result(state=State.WARN, summary="Cannot retrieve firmware information")
        return

    current_fw = section.results.current
    available_raw = section.results.available

    current_version = current_fw.version or "Unknown"
    current_build_str = current_fw.build_str

    critical_on_branch_change = section.config.critical_on_branch_change
    ok_if_unmatured_branch = section.config.ok_if_unmatured_branch

    current_tuple = current_fw.version_tuple
    current_major_int, current_minor_int, _, _ = current_tuple

    current_platform_id = current_fw.platform_id

    available_fw = []
    skipped_incompatible = 0
    for fw in available_raw:
        if fw.can_upgrade is False:
            skipped_incompatible += 1
            continue
        if current_platform_id:
            fw_platform = fw.platform_id
            if fw_platform and fw_platform != current_platform_id:
                skipped_incompatible += 1
                continue
        available_fw.append(fw)

    if not available_fw:
        details = f"Current: {current_version} build {current_build_str}"
        if skipped_incompatible:
            details += f" (skipped {skipped_incompatible} incompatible images)"
        yield Result(state=State.OK, summary=f"System is up to date: {current_version}", details=details)
        yield Metric("updates_available", 0)
        return

    available_fw.sort(key=lambda fw: fw.version_tuple)

    newer_updates = []
    recommended_fw = None
    highest_fw = None
    mature_updates = 0
    has_same_branch_updates = False
    next_branch_updates = []

    for fw in available_fw:
        fw_tuple = fw.version_tuple
        if fw_tuple <= current_tuple:
            continue

        newer_updates.append(fw)

        if fw.is_mature:
            mature_updates += 1

        fw_major, fw_minor, _, _ = fw_tuple

        if fw_major == current_major_int and fw_minor == current_minor_int:
            has_same_branch_updates = True
            if recommended_fw is None or fw_tuple < recommended_fw.version_tuple:
                recommended_fw = fw
        else:
            next_branch_updates.append(fw)

        if highest_fw is None or fw_tuple > highest_fw.version_tuple:
            highest_fw = fw

    if not newer_updates:
        yield Result(
            state=State.OK,
            summary=f"System is up to date: {current_version}",
            details=f"Current: {current_version} build {current_build_str}",
        )
        yield Metric("updates_available", 0)
        return

    updates_count = len(newer_updates)

    # Determine state
    if has_same_branch_updates:
        state = State.WARN
        state_reason = "Updates available"
    else:
        # only branch updates
        if ok_if_unmatured_branch and mature_updates == 0:
            state = State.OK
            state_reason = "Only immature branch updates available"
        else:
            state = State.CRIT if critical_on_branch_change else State.WARN
            state_reason = "Updates available (branch change)"

    # Summary + details
    summary = f"{state_reason}: {updates_count} update(s) available"

    # pick a recommended target
    target = recommended_fw or highest_fw or newer_updates[-1]
    target_version = target.version or "Unknown"
    target_build_str = target.build_str

    details_lines = [
        f"Current: {current_version} build {current_build_str}",
        f"Recommended: {target_version} build {target_build_str}",
    ]

    if not has_same_branch_updates and next_branch_updates:
        # show first branch candidate
        first = min(next_branch_updates, key=lambda fw: fw.version_tuple)
        details_lines.append(f"Branch candidate: {first.version or 'Unknown'} build {first.build_str}")

    if skipped_incompatible:
        details_lines.append(f"Skipped {skipped_incompatible} incompatible image(s)")

    yield Result(state=state, summary=summary, details="\n".join(details_lines))

    yield Metric("updates_available", updates_count)
    yield Metric("mature_updates", mature_updates)


check_plugin_fortios_firmware = CheckPlugin(
    name="fortios_firmware",
    service_name="FortiOS Firmware",
    sections=["fortios_firmware"],
    discovery_function=discover_fortios_firmware,
    check_function=check_fortios_firmware,
)
