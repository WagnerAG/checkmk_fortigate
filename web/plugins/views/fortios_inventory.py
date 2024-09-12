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

"""
Check_MK agent based checks to be used with agent_fortios Datasource

"""

from cmk.gui.i18n import _
from cmk.gui.type_defs import (
    ColumnSpec,
    PainterParameters,
    VisualLinkSpec,
)
from cmk.gui.views.store import multisite_builtin_views
from cmk.utils.type_defs import UserId

multisite_builtin_views.update(
    {
        "inv_fortios_devices": {
            "link_from": {},
            "packaged": False,
            "single_infos": [],
            "name": "inv_fortios_devices",
            "title": _("FortiOS devices"),
            "topic": "inventory",
            "sort_index": 10,
            "is_show_more": False,
            "description": "Hardware and software of Fortigate firewalls and the devices they manage\n",
            "icon": None,
            "add_context_to_title": True,
            "hidden": False,
            "hidebutton": True,
            "public": True,
            "datasource": "hosts",
            "browser_reload": 0,
            "layout": "table",
            "num_columns": 1,
            "column_headers": "pergroup",
            "mobile": False,
            "mustsearch": False,
            "force_checkboxes": False,
            "user_sortable": True,
            "play_sounds": False,
            "painters": [
                ColumnSpec(
                    name="host",
                    parameters=PainterParameters(color_choices=[]),
                    link_spec=VisualLinkSpec(type_name="views", name="inv_host"),
                    tooltip=None,
                    join_value=None,
                    column_title=None,
                ),
                ColumnSpec(
                    name="inv_hardware_system_manufacturer",
                    parameters=PainterParameters(use_short=False),
                    tooltip=None,
                    join_value=None,
                    column_title=None,
                ),
                ColumnSpec(
                    name="inv_software_os_version",
                    parameters=PainterParameters(use_short=False),
                    tooltip=None,
                    join_value=None,
                    column_title=None,
                ),
                ColumnSpec(
                    name="inv_software_os_build",
                    parameters=PainterParameters(use_short=False),
                    tooltip=None,
                    join_value=None,
                    column_title=None,
                ),
                ColumnSpec(
                    name="inv_hardware_system_serial",
                    parameters=PainterParameters(use_short=False),
                    tooltip=None,
                    join_value=None,
                    column_title=None,
                ),
                ColumnSpec(
                    name="inv_networking_fortios",
                    parameters=PainterParameters(use_short=False),
                    tooltip=None,
                    join_value=None,
                    column_title=None,
                ),
            ],
            "group_painters": [],
            "sorters": [],
            "context": {"hostregex": {"host_regex": "", "neg_host_regex": ""}, "inv_software_os_build": {"inv_software_os_build": ""}, "inv_software_os_version": {"inv_software_os_version": ""}, "inv_hardware_system_manufacturer": {"inv_hardware_system_manufacturer": "Fortinet"}, "has_inv": {"is_has_inv": "1"}},
            "owner": UserId.builtin(),
            "megamenu_search_terms": [],
        },
    }
)
