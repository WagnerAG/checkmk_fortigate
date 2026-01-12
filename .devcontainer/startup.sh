#!/bin/bash

find $OMD_ROOT/tmp/ -name "*.pid" -exec rm {} \;

source /omd/sites/cmk/.profile && $OMD_ROOT/bin/omd restart

# Add git config for gpg commit signing
git config --global gpg.format ssh && git config --global commit.gpgsign true