#!/bin/sh
# 
# check_myip.sh
# 
# Author: Márcio Pessoa <marcio@pessoa.eti.br>
# Contributors: none
# 
# Description:
#   This script is used to discover public IP address.
# 
# Example: 
#   check_myip.sh
# 
# Change log:
# 2015-06-30
#         * Scrash version.
# 

# Constant
PROGRAM=$(which wget)

# Checks if there is wget
if [ ! -f "$PROGRAM" ]; then
  echo "wget was not found."
  exit 10
fi

# Get public IP address
get_ip_addr() {
  STATUS=$($PROGRAM http://pessoa.eti.br/ip/ -q -O -)
  RETURN=$?
  check_get_ip_addr "$STATUS" $RETURN
}

# Check status from get_ip_addr
check_get_ip_addr() {
  STATUS=$1
  RETURN=$2
  case $RETURN in
    0)
      echo "$STATUS"
      exit 0
      ;;
    1)
      echo "Generic error code."
      exit 2
      ;;
    2)
      echo "Parse error---for instance, when parsing command-line options, the .wgetrc or .netrc..."
      exit 2
      ;;
    3)
      echo "File I/O error."
      exit 2
      ;;
    4)
      echo "Network failure."
      exit 2
      ;;
    5)
      echo "SSL verification failure."
      exit 2
      ;;
    6)
      echo "Username/password authentication failure."
      exit 2
      ;;
    7)
      echo "Protocol errors."
      exit 2
      ;;
    8)
      echo "Server issued an error response."
      exit 2
      ;;
    *)
      echo "Unknown error."
      exit 3
      ;;
  esac
}

# Check for input options
case "$1" in
  "")
    get_ip_addr;
    ;;
  *)
    echo "Usage: $0 without options."
    echo
    echo "Version: 0.01b"
    echo "Report bugs to: Marcio Pessoa <marcio@pessoa.eti.br>"
    ;;
esac
exit 0
