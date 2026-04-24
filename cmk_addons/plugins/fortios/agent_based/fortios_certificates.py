#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation in version 2. check_mk is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY; with-
# out even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more de-
# tails. You should have received a copy of the GNU General Public
# License along with GNU Make; see the file COPYING. If not, write
# to the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301 USA.

# WAGNER AG
# Developer: opensource@wagner.ch

"""
Check_MK agent based checks to be used with agent_fortios Datasource
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, List, Mapping, Optional

from pydantic import BaseModel, Field, model_validator

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
)


class CertificateSubject(BaseModel):
    C: Optional[str] = None
    ST: Optional[str] = None
    L: Optional[str] = None
    O: Optional[str] = None
    OU: Optional[str] = None
    CN: Optional[str] = None
    emailAddress: Optional[str] = None


class CertificateExtension(BaseModel):
    name: str
    data: str
    critical: bool = False


class Certificate(BaseModel):
    name: str
    comments: Optional[str] = None
    range: Optional[str] = None
    exists: bool = True
    type: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    valid_from: Optional[int] = None
    valid_to: Optional[int] = None
    valid_from_raw: Optional[str] = None
    valid_to_raw: Optional[str] = None
    subject: Optional[CertificateSubject] = None
    issuer: Optional[CertificateSubject] = None
    fingerprint: Optional[str] = None
    serial_number: Optional[str] = None
    is_built_in: Optional[bool] = None
    is_ca: Optional[bool] = None
    ext: Optional[List[CertificateExtension]] = None

    expires_at: Optional[datetime] = Field(default=None)
    seconds_until_expiry: Optional[int] = Field(default=None)
    state: State = Field(default=State.OK)

    @model_validator(mode="after")
    def compute_expiry(self) -> "Certificate":
        if self.valid_to is not None:
            self.expires_at = datetime.fromtimestamp(self.valid_to, tz=timezone.utc)
            delta = self.expires_at - datetime.now(timezone.utc)
            self.seconds_until_expiry = int(delta.total_seconds())
        return self

    def human_expiry(self) -> str:
        if self.expires_at is None or self.seconds_until_expiry is None:
            return "no expiry information"

        total_seconds = self.seconds_until_expiry
        prefix = "in "
        if total_seconds < 0:
            total_seconds = abs(total_seconds)
            prefix = "expired "

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        return (
            f"{self.expires_at.strftime('%Y-%m-%d %H:%M:%S %Z')} "
            f"({prefix}{days}d {hours}h {minutes}m)"
        )


class CertificateSet(BaseModel):
    certificates: List[Certificate]

    warn_days: int = 30
    crit_days: int = 7
    allowed_sources: list[str] = Field(default_factory=list)
    discover_ca: bool = True

    total: int = 0
    ok_count: int = 0
    warn_count: int = 0
    crit_count: int = 0
    relevant_certificates: List[Certificate] = Field(default_factory=list)

    @model_validator(mode="after")
    def classify_states(self) -> "CertificateSet":
        warn_threshold = self.warn_days * 86400
        crit_threshold = self.crit_days * 86400

        relevant_certs: list[Certificate] = []
        for cert in self.certificates:
            if self.allowed_sources and cert.source not in self.allowed_sources:
                continue
            if not self.discover_ca and cert.is_ca is True:
                continue
            relevant_certs.append(cert)

        self.relevant_certificates = relevant_certs
        self.total = len(relevant_certs)

        ok = warn = crit = 0
        for cert in relevant_certs:
            if cert.seconds_until_expiry is None:
                cert.state = State.CRIT
                crit += 1
                continue

            if cert.seconds_until_expiry <= 0:
                cert.state = State.CRIT
                crit += 1
                continue

            if cert.seconds_until_expiry < crit_threshold:
                cert.state = State.CRIT
                crit += 1
            elif cert.seconds_until_expiry < warn_threshold:
                cert.state = State.WARN
                warn += 1
            else:
                cert.state = State.OK
                ok += 1

        self.ok_count = ok
        self.warn_count = warn
        self.crit_count = crit
        return self

    @property
    def summary(self) -> str:
        return (
            f"Certificates: {self.total}, "
            f"OK: {self.ok_count}, WARN: {self.warn_count}, CRIT: {self.crit_count}"
        )

    @property
    def details(self) -> str:
        grouped_lines: dict[State, list[str]] = {
            State.CRIT: [],
            State.WARN: [],
            State.OK: [],
        }

        for cert in self.relevant_certificates:
            grouped_lines.setdefault(cert.state, []).append(
                f"[{cert.state.name}] {cert.name}: expires at {cert.human_expiry()}"
            )

        blocks: list[str] = []
        for state in (State.CRIT, State.WARN, State.OK):
            lines = grouped_lines.get(state, [])
            if lines:
                blocks.append("\n".join(lines))

        return "\n\n".join(blocks)


def parse_fortios_certificates(string_table: list[list[str]]) -> CertificateSet | None:
    try:
        json_data = json.loads(string_table[0][0])
    except (ValueError, IndexError, TypeError):
        return None

    if isinstance(json_data, list):
        certs_raw = json_data
    else:
        certs_raw = json_data.get("results", [])

    if not certs_raw:
        return None

    certificates = [Certificate(**item) for item in certs_raw]
    return CertificateSet(certificates=certificates)


agent_section_fortios_certificates = AgentSection(
    name="fortios_certificates",
    parse_function=parse_fortios_certificates,
)

DEFAULT_CERT_PARAMS = {
    "day_levels": ("fixed", (30, 7)),
    "source": ["factory", "user"],
    "discover_ca": True,
}


def _extract_day_levels(params: Mapping[str, Any]) -> tuple[int, int]:
    day_levels = params.get("day_levels", DEFAULT_CERT_PARAMS["day_levels"])
    if (
        isinstance(day_levels, tuple)
        and len(day_levels) == 2
        and day_levels[0] == "fixed"
        and isinstance(day_levels[1], tuple)
        and len(day_levels[1]) == 2
    ):
        return int(day_levels[1][0]), int(day_levels[1][1])
    return 30, 7


def _filtered_section(section: CertificateSet, params: Mapping[str, Any]) -> CertificateSet:
    warn_days, crit_days = _extract_day_levels(params)
    allowed_sources = params.get("source", DEFAULT_CERT_PARAMS["source"])
    discover_ca = params.get("discover_ca", DEFAULT_CERT_PARAMS["discover_ca"])

    return CertificateSet.model_validate(
        {
            "certificates": [cert.model_dump() for cert in section.certificates],
            "warn_days": warn_days,
            "crit_days": crit_days,
            "allowed_sources": allowed_sources,
            "discover_ca": discover_ca,
        }
    )


def discovery_fortios_certificates(section: CertificateSet) -> DiscoveryResult:
    if not section or not section.certificates:
        return
    yield Service()


def check_fortios_certificates(
    params: Mapping[str, Any],
    section: CertificateSet,
) -> CheckResult:
    if not section or not section.certificates:
        yield Result(state=State.UNKNOWN, summary="No certificate data available")
        return

    filtered = _filtered_section(section, params)

    if not filtered.relevant_certificates:
        yield Result(state=State.OK, summary="No relevant certificates after filtering")
        return

    overall_state = State.OK
    if filtered.crit_count > 0:
        overall_state = State.CRIT
    elif filtered.warn_count > 0:
        overall_state = State.WARN

    yield Result(
        state=overall_state,
        summary=filtered.summary,
        details=filtered.details,
    )

    yield Metric("cert_total", filtered.total)
    yield Metric("cert_ok", filtered.ok_count)
    yield Metric("cert_warn", filtered.warn_count)
    yield Metric("cert_crit", filtered.crit_count)


check_plugin_fortios_certificates = CheckPlugin(
    name="fortios_certificates",
    service_name="Certificate Expiry",
    sections=["fortios_certificates"],
    discovery_function=discovery_fortios_certificates,
    check_function=check_fortios_certificates,
    check_default_parameters=DEFAULT_CERT_PARAMS,
    check_ruleset_name="fortios_certificate_expiry",
)