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

# WAGNER AG
# Developer: opensource@wagner.ch

"""
Special agent for monitoring Fortinet Devices with FortiOS via REST API 2.x with Check_MK.

"""

from __future__ import annotations

import logging
import sys
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
import urllib3
from cmk.special_agents.v0_unstable.agent_common import (
    ConditionalPiggybackSection,
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import Args, create_default_argument_parser
from cmk.utils import password_store
from requests.adapters import HTTPAdapter

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
_LOGGER = logging.getLogger("agent_fortios")


_REST_VERSION: str = "v2"


@dataclass(frozen=True, kw_only=True)
class _SectionSpec:
    name: str
    path: str
    min_version: Optional[int]
    params: Mapping[str, str] | None = None
    piggyback: bool = False
    piggyback_section: str | None = None


_SECTIONS = [
    _SectionSpec(
        name="license",
        path="monitor/license/status",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="ntp",
        path="monitor/system/ntp/status",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="ipsec",
        path="monitor/vpn/ipsec?vdom=*",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="uptime",
        path="monitor/web-ui/state/select",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="ha_history",
        path="monitor/system/ha-history",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="ha_peer",
        path="monitor/system/ha-peer",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="interfaces",
        path="monitor/system/interface?vdom=*&include_aggregate=true&include_vlan=true",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="interfaces_cmdb",
        path="cmdb/system/interface",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="vdom_resources",
        path="monitor/system/vdom-resource?vdom=*",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="bgp_peer",
        path="monitor/router/bgp/neighbors",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="device_info",
        path="monitor/system/status",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="firmware",
        path="monitor/system/firmware",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="sslvpn",
        path="monitor/vpn/ssl?vdom=*",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="managed_switch",
        path="monitor/switch-controller/managed-switch/status",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="managed_switch_status",
        path="monitor/switch-controller/managed-switch/status",
        min_version=_REST_VERSION,
        piggyback=True,
        piggyback_section="switch",
    ),
    _SectionSpec(
        name="managed_switch_port_stats",
        path="monitor/switch-controller/managed-switch/port-stats",
        min_version=_REST_VERSION,
        piggyback=True,
        piggyback_section="switch",
    ),
    _SectionSpec(
        name="managed_switch",
        path="cmdb/switch-controller/managed-switch",
        min_version=_REST_VERSION,
        piggyback=True,
        piggyback_section="switch",
    ),
    ### Hangs for longer periods sometime, produces not output
    _SectionSpec(
        name="managed_switch_health_legacy",
        path="monitor/switch-controller/managed-switch/health",
        min_version=_REST_VERSION,
        piggyback=True,
        piggyback_section="switch",
    ),
    _SectionSpec(
        name="managed_switch_health",
        path="monitor/switch-controller/managed-switch/health-status",
        min_version=_REST_VERSION,
        piggyback=True,
        piggyback_section="switch",
    ),
    _SectionSpec(
        name="managed_ap",
        path="monitor/wifi/managed_ap",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="dhcp_scope",
        path="cmdb/system.dhcp/server",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="dhcp_lease",
        path="monitor/system/dhcp",
        min_version=_REST_VERSION,
    ),
    _SectionSpec(
        name="certificates",
        path="monitor/system/available-certificates?scope=*&with_remote=true&with_ca=true",
        min_version=_REST_VERSION,
    ),
]


def parse_arguments(argv: Sequence[str] | None) -> Args:
    parser = create_default_argument_parser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument(
        "--no-cert-check",
        action="store_true",
        help="""Disables the checking of the servers ssl certificate""",
    )
    parser.add_argument(
        "--cert-server-name",
        help="""Expect this as the servers name in the ssl certificate. Overrides '--no-cert-check'.""",
    )
    parser.add_argument(
        "--api-token",
        type=str,
        help=("Generate the API token through the CLI"),
    )
    # Firmware monitoring behaviour
    parser.add_argument(
        "--branch-change-critical",
        dest="branch_change_critical",
        action="store_true",
        default=True,
        help="Consider branch change critical (default)",
    )
    parser.add_argument(
        "--no-branch-change-critical",
        dest="branch_change_critical",
        action="store_false",
        help="Do not consider branch change critical",
    )
    parser.add_argument(
        "--ok-if-unmatured-branch",
        dest="ok_if_unmatured_branch",
        action="store_true",
        default=False,
        help="Return OK when only immature branch upgrades exist",
    )
    parser.add_argument(
        "--no-ok-if-unmatured-branch",
        dest="ok_if_unmatured_branch",
        action="store_false",
        help="Disable OK override for immature branch upgrades",
    )
    parser.add_argument("server", type=str, help="Hostname or IP address")
    return parser.parse_args(argv)


class JsonConcatenator:
    def __init__(self):
        self.store = {}

    def add_json(self, json_string, key=None):
        try:
            if not isinstance(json_string, dict):
                raise ValueError("JSON string must represent an object (dictionary).")
            if key:
                self.store[key] = json_string
            else:
                self.store.update(json_string)
        except ValueError as e:
            print(e)

    def get_value(self, key):
        return self.store.get(key)

    def get_store(self):
        return self.store


def _normalize_firmware_payload(payload):
    """Normalize firmware monitor payload across FortiOS versions.

    Some FortiOS releases wrap data in a "results" object while newer ones may
    expose "current" / "available" at the top level.
    """

    if not isinstance(payload, dict):
        return payload

    normalized = dict(payload)
    existing_results = normalized.get("results")
    results = dict(existing_results) if isinstance(existing_results, dict) else {}

    for key in ("current", "running", "installed", "active"):
        current_obj = normalized.get(key)
        if isinstance(current_obj, dict) and "current" not in results:
            results["current"] = current_obj
            break

    for key in ("available", "images", "upgrades", "upgrade_images", "firmwares"):
        available_list = normalized.get(key)
        if isinstance(available_list, list) and "available" not in results:
            results["available"] = available_list
            break

    if results:
        normalized["results"] = results

    normalized.setdefault("status", "success")
    return normalized


class SpecialAgentError(Exception):
    pass


class AuthError(SpecialAgentError):
    def __init__(self, message):
        super().__init__(message)
        sys.stderr.write(f"Connection error: {message}\n")
        sys.exit(2)


class APIEndpointNotFound(SpecialAgentError):
    def __init__(self, message):
        sys.stderr.write(f"HTTP status error: {message}\n")


class SectionError(SpecialAgentError):
    def __init__(self, message):
        sys.stdout.write(f"Section failure: {message}\n")


class HostNameValidationAdapter(HTTPAdapter):
    def __init__(self, host_name: str) -> None:
        super().__init__()
        self._reference_host_name = host_name

    def cert_verify(self, conn, url, verify, cert):
        conn.assert_hostname = self._reference_host_name
        return super().cert_verify(conn, url, verify, cert)


class _FortiOSSession:
    def __init__(self, server: str, port: int, cert_check: bool | str, timeout: int) -> None:
        self._session = requests.Session()
        self._base_url = f"https://{server}:{port}"
        self._port = port

        self._verify = True
        if cert_check is False:
            self._verify = False
            urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

        self._timeout = timeout
        self._x_auth_token = ""

    def post(self, path: str, headers: Mapping[str, str]) -> requests.Response:
        return self._session.post(
            f"{self._base_url}/api/{path}",
            headers=headers,
            verify=self._verify,
            timeout=self._timeout,
        )

    def get(
        self,
        path: str,
        headers: Mapping[str, str],
        params: Mapping[str, str] | None = None,
    ) -> requests.Response:
        return self._session.get(
            f"{self._base_url}/api/{path}",
            headers=headers,
            params=params,
            verify=self._verify,
            timeout=self._timeout,
        )


class FortiOS:
    def __init__(
        self,
        server: str,
        port: int,
        api_token: str,
        cert_check: bool,
        timeout: int,
    ) -> None:
        pw_id, pw_path = api_token.split(":")
        self._session = _FortiOSSession(server, port, cert_check, timeout)
        self._api_token = password_store.lookup(Path(pw_path), pw_id)

    def collect_section_data(self, spec: _SectionSpec, latest_version: str = _REST_VERSION) -> tuple[str, Mapping]:
        try:
            section_response = self._session.get(
                f"{latest_version}/{spec.path}",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self._api_token}",
                },
                params=spec.params,
            )
        except requests.exceptions.ConnectionError as e:
            _LOGGER.error(f"Login failed: {e}")
            raise AuthError(f"Login failed {e}") from e

        if section_response.status_code == 429:
            _LOGGER.error(f"Collecting section: {spec.name} failed. Reason: HTTP status 429; error: ({section_response.status_code}) {section_response.reason}")
            raise AuthError("IP address blacklisted or too many requests")

        if section_response.status_code != 200:
            _LOGGER.error(f"Collecting section: {spec.name} failed. Reason: HTTP status not 200; error: ({section_response.status_code}) {section_response.reason}")
            raise APIEndpointNotFound(f"Spec name: {spec.name} failed. Reason: HTTP status not 200; error: ({section_response.status_code}) {section_response.reason}")

        return section_response.json()


def _filter_applicable_sections(sections: Sequence[_SectionSpec], latest_version: str = _REST_VERSION) -> Iterator[_SectionSpec]:
    for spec in sections:
        if spec.min_version > latest_version:
            _LOGGER.error(
                "Collecting '%s' failed: '%s' > '%s'",
                spec.name,
                spec.min_version,
                latest_version,
            )
            continue

        yield spec


def agent_fortios(args: Args) -> int:
    fortios = FortiOS(
        args.server,
        args.port,
        args.api_token,
        args.cert_server_name or not args.no_cert_check,
        args.timeout,
    )

    # initialize value store for switch serial number mapping
    json_store = JsonConcatenator()

    for spec in _filter_applicable_sections(_SECTIONS):
        try:
            data = None
            data = fortios.collect_section_data(spec)

        except AuthError:
            # no use trying any other sections, abort entire run
            _LOGGER.error(f"Login failed while trying to collect {spec.name}: {spec.path}")
            sys.stdout.write("\n<<<>>>\n")
            break

        except Exception:
            _LOGGER.error(f"Collecting {spec.name} failed: {spec.path}")
            sys.stdout.write("\n<<<>>>\n")  # Hotfix: End previous-section. SectionError appends the error output to a working section otherwise.
            # CorrectSolution: SectionWriter+co should close its section on __exit__
            SectionError(f"Section error for spec: {spec.name} with path: {spec.path}")
            if args.debug:
                return 1
            else:
                continue  # data still contains values from earlier _spec, so w/o continue data gets outputed in wrong section

        # piggybackdata handling
        if spec.piggyback and spec.piggyback_section == "switch":
            # data = fortios.collect_section_data(spec) Redundant, already collected above
            json_store.add_json(data, spec.name)
        else:
            # Firmware payload normalization + inject monitoring configuration flags
            if spec.name == "firmware" and isinstance(data, dict):
                data = _normalize_firmware_payload(data)
                try:
                    cfg = data.get("config", {}) if isinstance(data.get("config"), dict) else {}
                    cfg.update(
                        {
                            "critical_on_branch_change": bool(getattr(args, "branch_change_critical", True)),
                            "ok_if_unmatured_branch": bool(getattr(args, "ok_if_unmatured_branch", False)),
                        }
                    )
                    data["config"] = cfg
                except Exception:
                    pass

            if isinstance(data, list):
                status_check = data[0]["status"]
            elif isinstance(data, dict):
                status_check = data["status"]
            else:
                status_check = None
                _LOGGER.error(f"Data is not a dict and not a list: {data} for spec: {spec.name}")

            if status_check == "success" and data is not None:
                with SectionWriter(f"fortios_{spec.name}") as writer:
                    writer.append_json(data)

    # Process piggyback data for switches
    switch_status = json_store.get_value("managed_switch_status")
    switch_status_data = switch_status.get("results")

    switch_health_legacy = json_store.get_value("managed_switch_health_legacy")
    switch_health_legacy_data = switch_health_legacy.get("results", {}) if switch_health_legacy else {}

    switch_health_new = json_store.get_value("managed_switch_health")
    switch_health_new_data = switch_health_new.get("results", []) if switch_health_new else []

    port_stats = json_store.get_value("managed_switch_port_stats")
    switch_port_stats = port_stats.get("results")

    managed_switch = json_store.get_value("managed_switch")
    switch_data = managed_switch.get("results")

    for switch in switch_status_data:
        if switch.get("status") != "Connected":
            _LOGGER.error(f"Switch status is not connected: {switch.get('status')}")
            continue
        switch_serial = switch.get("serial")
        switch_id = switch.get("switch-id")

        # map the ports stat data to the correct switch
        switch_port_stats_result = next(
            (item for item in switch_port_stats if item.get("serial") == switch_serial),
            None,
        )

        # map the switch data to the correct switch
        if "7.2" in managed_switch["version"]:
            # FortiOS 7.2: health endpoint returns dict keyed by serial
            switch_data_result = next((item for item in switch_data if item.get("switch-id") == switch_serial), None)
            switch_health_data_result = switch_health_legacy_data.get(switch_serial)

            with ConditionalPiggybackSection(switch["name"]):
                with SectionWriter("fortios_managed_switch_interface") as writer:
                    writer.append_json({"switch_port_stats": switch_port_stats_result, "switch_ports": switch, "switch_status": switch_data_result})
                with SectionWriter("fortios_managed_switch_health") as writer:
                    writer.append_json(switch_health_data_result)
        else:
            # FortiOS 7.4+: health-status endpoint returns list of objects
            switch_data_result = next((item for item in switch_data if item.get("switch-id") == switch_id), None)
            switch_health_data_result = next(
                (item for item in switch_health_new_data if item.get("serial") == switch_serial),
                None,
            )

            with ConditionalPiggybackSection(switch["switch-id"]):
                with SectionWriter("fortios_managed_switch_interface") as writer:
                    writer.append_json(
                        {
                            "switch_port_stats": switch_port_stats_result,
                            "switch_ports": switch,
                            "switch_status": switch_data_result,
                        }
                    )
                with SectionWriter("fortios_managed_switch_health") as writer:
                    writer.append_json(switch_health_data_result)

    return 0


def main() -> int:
    return special_agent_main(parse_arguments, agent_fortios)


if __name__ == "__main__":
    main()
