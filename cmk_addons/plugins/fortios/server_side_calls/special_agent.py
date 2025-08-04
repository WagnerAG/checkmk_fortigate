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

from collections.abc import Iterator
from typing import Any

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)
from pydantic import BaseModel


class Params(BaseModel):
    """params validator"""

    token: Secret | None = None
    port: int | None = None
    ssl: Any | None = None
    retries: int | None = None
    timeout: int | None = None
    debug: bool | None = None


def _agent_fortios_arguments(params: Params, host_config: HostConfig) -> Iterator[SpecialAgentCommand]:
    command_arguments: list[str | Secret] = []
    if params.token is not None:
        command_arguments += ["--api-token-id", params.token]
    if params.port is not None:
        command_arguments += ["--port", str(params.port)]
    if params.timeout is not None:
        command_arguments += ["--timeout", str(params.timeout)]
    if params.retries is not None:
        command_arguments += ["--retries", str(params.retries)]
    if params.ssl is not None:
        command_arguments += ["--no-cert-check"]
    if params.debug:
        command_arguments += ["--debug"]

    command_arguments.append(host_config.primary_ip_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_fortios = SpecialAgentConfig(
    name="fortios",
    parameter_parser=Params.model_validate,
    commands_function=_agent_fortios_arguments,
)
