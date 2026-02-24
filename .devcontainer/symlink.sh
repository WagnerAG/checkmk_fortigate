#!/bin/bash

NAME=$(python3 -c 'print(eval(open("package").read())["name"])')
WORKSPACE=$(pwd)

ln -sv $WORKSPACE/cmk_addons/plugins/$NAME $OMD_ROOT/local/lib/python3/cmk_addons/plugins/$NAME

rm -rfv $OMD_ROOT/local/lib/python3/cmk
ln -sv $WORKSPACE/lib $OMD_ROOT/local/lib/python3/cmk

rm -rfv $OMD_ROOT/local/share/check_mk
ln -sv $WORKSPACE/plugins_legacy $OMD_ROOT/local/share/check_mk

source /omd/sites/cmk/.profile && echo 'cmkadmin' | /omd/sites/cmk/bin/cmk-passwd -i cmkadmin

echo "▹ Starting OMD... "
omd restart