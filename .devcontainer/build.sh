#!/bin/bash

NAME=$(python3 -c 'print(eval(open("package").read())["name"])')
VERSION=$(python3 -c 'print(eval(open("package").read())["version"])')
rm /omd/sites/cmk/var/check_mk/packages/${NAME} \
   /omd/sites/cmk/var/check_mk/packages_local/${NAME}-*.mkp ||:

mkp -v package package 2>&1 | sed '/Installing$/Q' ||:

cp /omd/sites/cmk/var/check_mk/packages_local/$NAME-$VERSION.mkp .

mkp inspect $NAME-$VERSION.mkp

# Set Outputs for GitHub Workflow steps
if [ -n "$GITHUB_WORKSPACE" ]; then
    echo "::set-output name=pkgfile::$(ls *.mkp)"
    echo "::set-output name=pkgname::${NAME}"
    VERSION=$(python -c 'print(eval(open("package").read())["version"])')
    echo "::set-output name=pkgversion::$VERSION"
fi