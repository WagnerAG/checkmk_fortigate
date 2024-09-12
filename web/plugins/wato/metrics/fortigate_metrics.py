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
Check_MK metric definitions for Fortigate checks

"""

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics.utils import metric_info

metric_info["fortigate_ap_cpu_util"] = {
    "title": _("AP CPU utilization"),
    "unit": "%",
    "color": "26/a",
}

metric_info["fortigate_ap_memory_util"] = {
    "title": _l("AP Memory utilization"),
    "unit": "%",
    "color": "26/a",
}