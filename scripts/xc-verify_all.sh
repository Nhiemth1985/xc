#!/bin/sh
#
# xc-verify_all.sh
#
# Author: Marcio Pessoa <marcio.pessoa@gmail.com>
# Contributors: none
#
# Description:
#   This script is used to check source code of all available devices.
#
# Example:
#   xc-verify_all.sh
#
# Change log:
# 2019-01-12
#         * Scrash version.
#

for id in $(xc list --verbosity=1); do
  if ! xc verify --verbosity=0 --id "$id"; then
    echo "$id: Fail"
  fi
done
