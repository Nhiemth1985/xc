#!/bin/bash
# 
# xc
# 
# Author: Márcio Pessoa <marcio.pessoa@sciemon.com>
# Contributors: none
# 
# Description:
#   Start up script file
# 
# Example:
#   xc -h
# 
# Change log:
# 2017-05-22
#          * Bug fix: Supress SDL verbose messages.
# 
# 2017-03-05
#          * Bug fix: --verbosity option was using an unmutable value (4).
# 
# 2017-02-03
#         * First version.
#

readonly WORK_DIR='/opt/sciemon/xc'
readonly WORK_FILE='xc.pyc'

# Default values
command="gui"
verbosity=4

# Enable full screen mode on xc appliance
case "$HOSTNAME" in
  'xCm1')
    arguments=(--fullscreen)
    ;;
  'xCm2')
    arguments=(--fullscreen --screen 480x320)
    ;;
  *)
    arguments=()
    ;;
esac

# Identify user defined verbosity
declare -a args=($@)
for (( i = 0; i < ${#args[*]}; i++ )); do
  if [ "${args[$i]}" == "--verbosity" ]; then
    verbosity=${args[$i+1]}
    break
  fi
  if [ "$(echo "${args[$i]}" | cut -d '=' -f 1)" == "--verbosity" ]; then
    verbosity=$(echo "${args[$i]}" | cut -d '=' -f 2)
    break
  fi
done

# Apply desired command
if [ "$#" -eq 0 ]; then
  python "$WORK_DIR"/"$WORK_FILE" "$command" "${arguments[@]}" \
    --verbosity="$verbosity" | \
    grep -v 'SDL_'
else
  python "$WORK_DIR"/"$WORK_FILE" "$@" \
    --verbosity="$verbosity" | \
    grep -v 'SDL_'
fi
