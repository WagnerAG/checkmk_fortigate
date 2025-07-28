#!/bin/bash

find $OMD_ROOT/tmp/ -name "*.pid" -exec rm {} \;

source /omd/sites/cmk/.profile && $OMD_ROOT/bin/omd restart