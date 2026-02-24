#!/bin/bash

find $OMD_ROOT/tmp/ -name "*.pid" -exec rm {} \;

source /omd/sites/cmk/.profile && $OMD_ROOT/bin/omd restart

echo "export GPG_TTY=$(tty)" >> /omd/sites/cmk/.bashrc

# Add git config for gpg commit signing
git config --global commit.gpgsign true
