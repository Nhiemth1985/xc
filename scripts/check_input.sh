#!/bin/sh
#
# check_input.sh
#
# Author: Marcio Pessoa <marcio.pessoa@gmail.com>
# Contributors: none
#
# Description:
#   This script is used to check available input devices.
#
# Example:
#   check_input.sh keyboard
#   check_input.sh mouse
#
# Change log:
# 2017-06-13
#         * Scrash version.
#

device=$1

lsusb -v 2>/dev/null | \
  grep bInterfaceProtocol | \
  grep -i "$device" \
  > /dev/null 2>&1

exit $?
