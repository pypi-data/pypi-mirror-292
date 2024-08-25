#!/bin/sh

# Access folder
script_path=$(readlink -f "${0}")
test_path=$(readlink -f "${script_path%/*}")
cd "${test_path}/"

# Configure tests
set -ex

# Configure environment
(
  # Configure versions
  export DEBUG_UPDATES_DISABLE=''
  export DEBUG_VERSION_FAKE='2.0.0'

  # Run tests
  pexpect-executor --version
  pexpect-executor --update-check
  DEBUG_UPDATES_DISABLE=true pexpect-executor --update-check
  FORCE_COLOR=1 pexpect-executor --update-check
  NO_COLOR=1 pexpect-executor --update-check
  FORCE_COLOR=1 PYTHONIOENCODING=ascii pexpect-executor --update-check
  FORCE_COLOR=1 COLUMNS=40 pexpect-executor --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE='' pexpect-executor --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true pexpect-executor --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.1 pexpect-executor --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.2 pexpect-executor --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_OFFLINE=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.3 pexpect-executor --update-check
  FORCE_COLOR=1 DEBUG_UPDATES_DAILY=true DEBUG_VERSION_FAKE=0.0.2 DEBUG_UPDATES_FAKE=0.0.3 pexpect-executor -- echo 'Test'
  FORCE_COLOR=1 pexpect-executor -- echo 'Test'
)
