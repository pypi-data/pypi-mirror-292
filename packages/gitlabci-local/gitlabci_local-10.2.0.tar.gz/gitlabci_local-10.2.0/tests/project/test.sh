#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Run tests
gcil -p
gcil -H -p
gcil 'Job 2' && exit 1 || true
gcil -e CI_VARIABLE_DIR=. 'Job 2'
CI_VARIABLE_DIR=. gcil 'Job 2' && exit 1 || true
CI_VARIABLE_DIR=. gcil -e CI_VARIABLE_DIR 'Job 2'
gcil 'Job 3'
gcil 'Job 4'
gcil -e CI_CONSTANT_PRE_DIR=. -e CI_CONSTANT_POST_DIR=. 'Job 3'
