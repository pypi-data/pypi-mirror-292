#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil --settings
! type sudo >/dev/null 2>&1 || sudo -E env PYTHONPATH="${PYTHONPATH}" gcil --settings
gcil --set && exit 1 || true
gcil --set GROUP && exit 1 || true
gcil --set GROUP KEY && exit 1 || true
gcil --set package test 1
gcil --set package test 0
gcil --set package test UNSET
gcil --set updates enabled NaN
gcil --version
gcil --set updates enabled UNSET
