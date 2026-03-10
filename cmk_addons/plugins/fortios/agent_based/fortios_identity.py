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

"""FortiOS device identity (model + serial) as separate services.

This is a small convenience check requested to split model and serial into
individual services. Data is taken from the existing `fortios_device_info`
section produced by the FortiOS special agent.
"""

from __future__ import annotations

from cmk.agent_based.v2 import CheckPlugin, Result, Service, State


def _extract_device_info(section):
    # section is a mapping: {hostname: DeviceInfo}
    try:
        _, info = next(iter(section.items()))
    except Exception:
        return None
    return info


def discover_fortios_identity(section):
    info = _extract_device_info(section)
    if not info:
        return

    # Model
    model_name = None
    model = None
    hostname = None
    try:
        if getattr(info, "results", None) is not None:
            model_name = getattr(info.results, "model_name", None)
            model = getattr(info.results, "model", None)
            hostname = getattr(info.results, "hostname", None)
    except Exception:
        pass

    if model_name or model:
        yield Service(item="Model")

    # Serial
    serial = getattr(info, "serial", None)
    if serial:
        yield Service(item="Serial")


def check_fortios_identity(item, section):
    info = _extract_device_info(section)
    if not info:
        yield Result(state=State.UNKNOWN, summary="No data received")
        return

    serial = getattr(info, "serial", None)

    model_name = None
    model = None
    hostname = None
    try:
        if getattr(info, "results", None) is not None:
            model_name = getattr(info.results, "model_name", None)
            model = getattr(info.results, "model", None)
            hostname = getattr(info.results, "hostname", None)
    except Exception:
        pass

    if item == "Model":
        if not (model_name or model):
            yield Result(state=State.UNKNOWN, summary="Model information not available")
            return
        summary = " ".join([x for x in [model_name, model] if x]) or "Unknown"
        details = f"Hostname: {hostname}" if hostname else None
        yield Result(state=State.OK, summary=summary, details=details)

    elif item == "Serial":
        if not serial:
            yield Result(state=State.UNKNOWN, summary="Serial number not available")
            return
        yield Result(state=State.OK, summary=str(serial))

    else:
        yield Result(state=State.UNKNOWN, summary=f"Unknown item: {item}")


check_plugin_fortios_identity = CheckPlugin(
    name="fortios_identity",
    service_name="FortiOS %s",
    sections=["fortios_device_info"],
    discovery_function=discover_fortios_identity,
    check_function=check_fortios_identity,
)
