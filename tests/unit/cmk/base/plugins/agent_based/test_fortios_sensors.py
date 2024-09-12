#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Metric,
    Result,
    State,
)
from cmk.base.plugins.agent_based.fortios_sensors import (
    Sensor,
    Thresholds,
    check_fortios_sensors,
    parse_fortios_sensors,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [
                [
                    '{"http_method": "GET",  "results": [    {      "id": "voltage.ad_+3.3v",      "name": "AD_+3.3V",      "type": "voltage",      "value": 3.34085011482239,      "alarm": false,      "thresholds": {        "lower_non_recoverable": 2.7870500087738,        "lower_critical": 2.85095000267029,        "lower_non_critical": 2.93615007400513,        "upper_non_critical": 3.70295000076294,        "upper_critical": 3.80944991111755,        "upper_non_recoverable": 3.87334990501404      }    },    {      "id": "voltage.ad_+5v",      "name": "AD_+5V",      "type": "voltage",      "value": 5.09210014343262,      "alarm": false,      "thresholds": {        "lower_non_recoverable": 4.22270011901856,        "lower_critical": 4.28709983825684,        "lower_non_critical": 4.44810009002686,        "upper_non_critical": 5.6395001411438,        "upper_critical": 5.80049991607666,        "upper_non_recoverable": 5.89709997177124      }    },    {      "id": "voltage.ad_+12v",      "name": "AD_+12V",      "type": "voltage",      "value": 12.0579996109009,      "alarm": false,      "thresholds": {        "lower_non_recoverable": 9.51700019836426,        "lower_critical": 9.82499980926514,        "lower_non_critical": 10.3640003204346,        "upper_non_critical": 13.6750001907349,        "upper_critical": 14.4449996948242,        "upper_non_recoverable": 14.8299999237061      }    },    {      "id": "voltage.p3v3_aux",      "name": "P3V3_AUX",      "type": "voltage",      "value": 3.31955003738403,      "alarm": false,      "thresholds": {        "lower_non_recoverable": 2.7870500087738,        "lower_critical": 2.85095000267029,        "lower_non_critical": 2.93615007400513,        "upper_non_critical": 3.70295000076294,        "upper_critical": 3.80944991111755,        "upper_non_recoverable": 3.87334990501404      }    }  ],  "vdom": "root",  "path": "system",  "name": "sensor-info",  "action": "",  "status": "success",  "serial": "FG1K0FTB22900191",  "version": "v7.2.7",  "build": 1577}'
                ]
            ],
            [
                Sensor(id="voltage.ad_+3.3v", name="AD_+3.3V", type="voltage", value=3.34085011482239, alarm=False, thresholds=Thresholds(upper_non_critical=3.70295000076294, upper_critical=3.80944991111755, upper_non_recoverable=3.87334990501404, lower_non_critical=2.93615007400513, lower_critical=2.85095000267029, lower_non_recoverable=2.7870500087738)),
                Sensor(id="voltage.ad_+5v", name="AD_+5V", type="voltage", value=5.09210014343262, alarm=False, thresholds=Thresholds(upper_non_critical=5.6395001411438, upper_critical=5.80049991607666, upper_non_recoverable=5.89709997177124, lower_non_critical=4.44810009002686, lower_critical=4.28709983825684, lower_non_recoverable=4.22270011901856)),
                Sensor(id="voltage.ad_+12v", name="AD_+12V", type="voltage", value=12.0579996109009, alarm=False, thresholds=Thresholds(upper_non_critical=13.6750001907349, upper_critical=14.4449996948242, upper_non_recoverable=14.8299999237061, lower_non_critical=10.3640003204346, lower_critical=9.82499980926514, lower_non_recoverable=9.51700019836426)),
                Sensor(id="voltage.p3v3_aux", name="P3V3_AUX", type="voltage", value=3.31955003738403, alarm=False, thresholds=Thresholds(upper_non_critical=3.70295000076294, upper_critical=3.80944991111755, upper_non_recoverable=3.87334990501404, lower_non_critical=2.93615007400513, lower_critical=2.85095000267029, lower_non_recoverable=2.7870500087738)),
            ],
        ),
        (
            [[]],
            None,
        ),
    ],
)
def test_parse_fortios_sensors(string_table: list[list[str]] | list[list], expected_section: dict[str, Sensor] | None) -> None:
    assert parse_fortios_sensors(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            [
                Sensor(id="voltage.ad_+3.3v", name="AD_+3.3V", type="voltage", value=3.34085011482239, alarm=False, thresholds=Thresholds(upper_non_critical=3.70295000076294, upper_critical=3.80944991111755, upper_non_recoverable=3.87334990501404, lower_non_critical=2.93615007400513, lower_critical=2.85095000267029, lower_non_recoverable=2.7870500087738)),
                Sensor(id="voltage.p3v3_aux", name="P3V3_AUX", type="voltage", value=3.31955003738403, alarm=False, thresholds=Thresholds(upper_non_critical=3.70295000076294, upper_critical=3.80944991111755, upper_non_recoverable=3.87334990501404, lower_non_critical=2.93615007400513, lower_critical=2.85095000267029, lower_non_recoverable=2.7870500087738)),
                Sensor(id="voltage.ad_+5v", name="AD_+5V", type="voltage", value=5.09210014343262, alarm=False, thresholds=Thresholds(upper_non_critical=5.6395001411438, upper_critical=5.80049991607666, upper_non_recoverable=5.89709997177124, lower_non_critical=4.44810009002686, lower_critical=4.28709983825684, lower_non_recoverable=4.22270011901856)),
                Sensor(id="voltage.ad_+12v", name="AD_+12V", type="voltage", value=12.0579996109009, alarm=False, thresholds=Thresholds(upper_non_critical=13.6750001907349, upper_critical=14.4449996948242, upper_non_recoverable=14.8299999237061, lower_non_critical=10.3640003204346, lower_critical=9.82499980926514, lower_non_recoverable=9.51700019836426)),
            ],
            [
                Result(state=State.OK, summary="No hardware alarms"),
                Metric("alarm_count", 0.0),
            ],
        ),
        (
            [
                Sensor(id="voltage.ad_+3.3v", name="AD_+3.3V", type="voltage", value=3.34085011482239, alarm=True, thresholds=Thresholds(upper_non_critical=3.70295000076294, upper_critical=3.80944991111755, upper_non_recoverable=3.87334990501404, lower_non_critical=2.93615007400513, lower_critical=2.85095000267029, lower_non_recoverable=2.7870500087738)),
                Sensor(id="voltage.p3v3_aux", name="P3V3_AUX", type="voltage", value=3.31955003738403, alarm=False, thresholds=Thresholds(upper_non_critical=3.70295000076294, upper_critical=3.80944991111755, upper_non_recoverable=3.87334990501404, lower_non_critical=2.93615007400513, lower_critical=2.85095000267029, lower_non_recoverable=2.7870500087738)),
                Sensor(id="voltage.ad_+5v", name="AD_+5V", type="voltage", value=5.09210014343262, alarm=True, thresholds=Thresholds(upper_non_critical=5.6395001411438, upper_critical=5.80049991607666, upper_non_recoverable=5.89709997177124, lower_non_critical=4.44810009002686, lower_critical=4.28709983825684, lower_non_recoverable=4.22270011901856)),
                Sensor(id="voltage.ad_+12v", name="AD_+12V", type="voltage", value=12.0579996109009, alarm=False, thresholds=Thresholds(upper_non_critical=13.6750001907349, upper_critical=14.4449996948242, upper_non_recoverable=14.8299999237061, lower_non_critical=10.3640003204346, lower_critical=9.82499980926514, lower_non_recoverable=9.51700019836426)),
            ],
            [
                Result(state=State.CRIT, summary="Alarms: Name: AD_+3.3V, Type: voltage, Value: 3.34085011482239 Name: AD_+5V, Type: voltage, Value: 5.09210014343262"),
                Metric("alarm_count", 2.0),
            ],
        ),
    ],
)
def test_check_fortios_sensors(section, expected_check_result: list) -> None:
    actual_check_result = list(check_fortios_sensors(section))
    assert actual_check_result == expected_check_result
