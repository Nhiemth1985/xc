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
# 2018-07-18
#          * Bug fix: Not returning the xc.pyc exit status.
#          * Bug fix: Not undestanding -v option.
#
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

# Identify user defined verbosity
declare -a args=($@)
for (( i = 0; i < ${#args[*]}; i++ )); do
  if [ "${args[$i]}" == "--verbosity" ] || [ "${args[$i]}" == "-v" ]; then
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
  python "$WORK_DIR"/"$WORK_FILE" "$command" \
    --verbosity="$verbosity" | \
    grep -v 'SDL_'
  exit ${PIPESTATUS[0]}
else
  python "$WORK_DIR"/"$WORK_FILE" "$@" \
    --verbosity="$verbosity" | \
    grep -v 'SDL_'
  exit ${PIPESTATUS[0]}
fi
