#!/bin/sh

for id in $(xc list --verbosity=1); do
  if ! xc verify --verbosity=0 --id "$id"; then
    echo "$id: Fail"
  fi
done
