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

"""FortiOS system information service.

The FortiOS package historically provided inventory information (HW/SW) via the
'fortios_device_info' section. This check adds a regular service that shows the
current FortiOS version/build and basic device identity.

It mirrors the behaviour of the standalone 'fortigate_system' service from the
fortigate_firmware extension, but reuses the existing FortiOS agent output.
"""

from __future__ import annotations

from cmk.agent_based.v2 import CheckPlugin, Metric, Result, Service, State


def discover_fortios_system(section):
    if section:
        yield Service()


def check_fortios_system(section):
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data received")
        return

    # section is a mapping: {hostname: DeviceInfo}
    try:
        _, info = next(iter(section.items()))
    except Exception:
        yield Result(state=State.UNKNOWN, summary="Unexpected data format")
        return

    version = getattr(info, "version", None) or "Unknown"
    build = getattr(info, "build", None) or "Unknown"
    serial = getattr(info, "serial", None) or "Unknown"

    model_name = "Unknown"
    model = "Unknown"
    hostname = "Unknown"
    try:
        if getattr(info, "results", None) is not None:
            model_name = getattr(info.results, "model_name", None) or model_name
            model = getattr(info.results, "model", None) or model
            hostname = getattr(info.results, "hostname", None) or hostname
    except Exception:
        pass

    summary = f"Version {version} Build {build}"
    details = f"Model: {model_name} {model}, Hostname: {hostname}, Serial: {serial}"

    yield Result(state=State.OK, summary=summary, details=details)

    # Metrics (optional)
    try:
        version_clean = str(version).lstrip("v")
        parts = version_clean.split(".")
        if len(parts) >= 2:
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2]) if len(parts) > 2 else 0
            yield Metric("version_numeric", major * 10000 + minor * 100 + patch)
        if str(build).isdigit():
            yield Metric("build_number", int(build))
    except Exception:
        pass


check_plugin_fortios_system = CheckPlugin(
    name="fortios_system",
    service_name="FortiOS System",
    sections=["fortios_device_info"],
    discovery_function=discover_fortios_system,
    check_function=check_fortios_system,
)
