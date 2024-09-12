#!/bin/bash

for DIR in 'agents' 'checkman' 'checks' 'doc' 'inventory' 'notifications' 'pnp-templates' 'web'; do
    rm -rfv $OMD_ROOT/local/share/check_mk/$DIR
    ln -sv $WORKSPACE/$DIR $OMD_ROOT/local/share/check_mk/$DIR
done;

rm -rfv $OMD_ROOT/local/lib/check_mk/notification_plugins
ln -sv $WORKSPACE/notification_plugins $OMD_ROOT/local/lib/check_mk/notification_plugins

mkdir -p $OMD_ROOT/local/lib/check_mk/gui/plugins/wato/
mkdir -p $OMD_ROOT/local/lib/check_mk/gui/plugins/wato/check_parameters
ln -sv $WORKSPACE/agent_based_check_parameters $OMD_ROOT/local/lib/check_mk/gui/plugins/wato/check_parameters

rm -rfv $OMD_ROOT/local/lib/check_mk/special_agents
ln -sv $WORKSPACE/agent_based_special $OMD_ROOT/local/lib/check_mk/special_agents

rm -rfv $OMD_ROOT/local/lib/python3/cmk/base/plugins/agent_based
ln -sv $WORKSPACE/agent_based $OMD_ROOT/local/lib/python3/cmk/base/plugins/agent_based

rm -rfv $OMD_ROOT/local/tmp
ln -sv $WORKSPACE/temp $OMD_ROOT/local/tmp

rm -rfv $OMD_ROOT/local/lib/check_mk/base/cee/plugins/bakery
mkdir -p $OMD_ROOT/local/lib/python3/cmk/base/cee/plugins
ln -sv $WORKSPACE/bakery $OMD_ROOT/local/lib/python3/cmk/base/cee/plugins/bakery

source /omd/sites/cmk/.profile && echo 'cmkadmin' | /omd/sites/cmk/bin/cmk-passwd -i cmkadmin

echo "▹ Starting OMD... "
omd restart