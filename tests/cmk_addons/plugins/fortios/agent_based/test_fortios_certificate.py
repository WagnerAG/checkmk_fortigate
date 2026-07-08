#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU  General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# WAGNER AG
# Developer: opensource@wagner.ch

from typing import Mapping

import pytest
from datetime import datetime, timedelta, timezone
from cmk.agent_based.v2 import Metric, Result, Service, State

from cmk_addons.plugins.fortios.agent_based.fortios_certificates import (
    DEFAULT_CERT_PARAMS,
    Certificate,
    CertificateSet,
    check_fortios_certificates,
    discovery_fortios_certificates,
    parse_fortios_certificates,
)


def _canonicalize_certificate_set(section: CertificateSet | None) -> CertificateSet | None:
    if section is None:
        return None

    runtime_fields = {"expires_at", "seconds_until_expiry", "state"}
    normalized_certs = []
    for cert in section.certificates:
        cert_data = cert.model_dump(exclude=runtime_fields)
        normalized_certs.append(Certificate.model_validate(cert_data))

    return CertificateSet.model_validate(
        {
            "certificates": [cert.model_dump() for cert in normalized_certs],
            "warn_days": section.warn_days,
            "crit_days": section.crit_days,
            "allowed_sources": section.allowed_sources,
            "discover_ca": section.discover_ca,
        }
    )


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"results": ['
                    '{"name": "Fortinet_CA_SSL", "source": "factory", "is_ca": true, "valid_to": 2007640248, "exists": true}, '
                    '{"name": "example-cert-2024", "source": "user", "is_ca": false, "valid_to": 1724371199, "exists": true}'
                    ']}'
                ]
            ],
            CertificateSet(
                certificates=[
                    Certificate(
                        name="Fortinet_CA_SSL",
                        source="factory",
                        is_ca=True,
                        valid_to=2007640248,
                        exists=True,
                    ),
                    Certificate(
                        name="example-cert-2024",
                        source="user",
                        is_ca=False,
                        valid_to=1724371199,
                        exists=True,
                    ),
                ]
            ),
        ),
        (
            [[]],
            None,
        ),
    ],
)
def test_parse_fortios_certificates(
    string_table: list[list[str]] | list[list],
    expected_section: CertificateSet | None,
) -> None:
    parsed = parse_fortios_certificates(string_table)
    assert _canonicalize_certificate_set(parsed) == _canonicalize_certificate_set(expected_section)


@pytest.mark.parametrize(
    "section, expected_discovery_result",
    [
        (
            CertificateSet(
                certificates=[
                    Certificate(
                        name="Fortinet_CA_SSL",
                        source="factory",
                        is_ca=True,
                        valid_to=2007640248,
                        exists=True,
                    )
                ]
            ),
            [Service()],
        ),
        (
            None,
            [],
        ),
    ],
)
def test_discovery_fortios_certificates(
    section: CertificateSet | None,
    expected_discovery_result: list[Service],
) -> None:
    assert list(discovery_fortios_certificates(section)) == expected_discovery_result


@pytest.mark.parametrize(
    "section, params, expected_check_result",
    [
        (
            CertificateSet(
                certificates=[
                    Certificate(
                        name="user_ok_cert",
                        source="user",
                        is_ca=False,
                        valid_to=2208988800,
                        exists=True,
                    ),
                ]
            ),
            {
                "day_levels": ("fixed", (1000, 500)),
                "source": ["user"],
                "discover_ca": True,
            },
            [
                Result(
                    state=State.OK,
                    summary="Certificates: 1, OK: 1, WARN: 0, CRIT: 0",
                    details="[OK] user_ok_cert: expires at 2040-01-01 00:00:00 UTC (in "
                    + Certificate(
                        name="user_ok_cert",
                        source="user",
                        is_ca=False,
                        valid_to=2208988800,
                        exists=True,
                    ).human_expiry().split("(in ", 1)[1],
                ),
                Metric("cert_total", 1),
                Metric("cert_ok", 1),
                Metric("cert_warn", 0),
                Metric("cert_crit", 0),
            ],
        ),
    ],
)
def test_check_fortios_certificates_basic(
    section: CertificateSet,
    params: Mapping[str, object],
    expected_check_result: list,
) -> None:
    actual_check_result = list(check_fortios_certificates(params, section))
    assert actual_check_result == expected_check_result


def test_check_fortios_certificates_filters_source_and_ca() -> None:
    section = CertificateSet(
        certificates=[
            Certificate(
                name="factory_non_ca",
                source="factory",
                is_ca=False,
                valid_to=2208988800,
                exists=True,
            ),
            Certificate(
                name="user_ca",
                source="user",
                is_ca=True,
                valid_to=2208988800,
                exists=True,
            ),
            Certificate(
                name="user_non_ca",
                source="user",
                is_ca=False,
                valid_to=2208988800,
                exists=True,
            ),
        ]
    )

    params = {
        "day_levels": ("fixed", (1000, 500)),
        "source": ["user"],
        "discover_ca": False,
    }

    actual_check_result = list(check_fortios_certificates(params, section))

    service_result = actual_check_result[0]
    assert service_result.state == State.OK
    assert service_result.summary == "Certificates: 1, OK: 1, WARN: 0, CRIT: 0"
    assert "user_non_ca" in service_result.details
    assert "factory_non_ca" not in service_result.details
    assert "user_ca" not in service_result.details


def test_check_fortios_certificates_groups_details_by_state() -> None:
    now = datetime.now(timezone.utc)
    section = CertificateSet(
        certificates=[
            Certificate(
                name="expired-demo-cert",
                source="user",
                is_ca=False,
                valid_to=int((now - timedelta(days=100)).timestamp()),
                exists=True,
            ),
            Certificate(
                name="warning-demo-cert",
                source="user",
                is_ca=False,
                valid_to=int((now + timedelta(days=750)).timestamp()),
                exists=True,
            ),
            Certificate(
                name="ok-demo-cert",
                source="user",
                is_ca=False,
                valid_to=int((now + timedelta(days=2600)).timestamp()),
                exists=True,
            ),
        ]
    )

    params = {
        "day_levels": ("fixed", (1000, 500)),
        "source": ["user"],
        "discover_ca": True,
    }

    actual_check_result = list(check_fortios_certificates(params, section))
    details = actual_check_result[0].details

    assert "[CRIT] expired-demo-cert" in details
    assert "[WARN] warning-demo-cert" in details
    assert "[OK] ok-demo-cert" in details
    assert details.index("[CRIT] expired-demo-cert") < details.index("[WARN] warning-demo-cert")
    assert details.index("[WARN] warning-demo-cert") < details.index("[OK] ok-demo-cert")
    assert "\n\n[WARN]" in details
    assert "\n\n[OK]" in details


def test_check_fortios_certificates_returns_ok_if_no_relevant_certificates() -> None:
    section = CertificateSet(
        certificates=[
            Certificate(
                name="factory_ca",
                source="factory",
                is_ca=True,
                valid_to=2007640248,
                exists=True,
            )
        ]
    )

    params = {
        "day_levels": ("fixed", (1000, 500)),
        "source": ["user"],
        "discover_ca": False,
    }

    actual_check_result = list(check_fortios_certificates(params, section))

    assert actual_check_result == [
        Result(state=State.OK, summary="No relevant certificates after filtering")
    ]


def test_check_fortios_certificates_returns_unknown_if_no_data() -> None:
    actual_check_result = list(check_fortios_certificates(DEFAULT_CERT_PARAMS, None))

    assert actual_check_result == [
        Result(state=State.UNKNOWN, summary="No certificate data available")
    ]