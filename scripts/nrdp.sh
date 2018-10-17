#!/bin/sh
# 
# nrdp.sh
# 
# Author: Márcio Pessoa <marcio.pessoa@gmail.com>
# Contributors: none
# 
# Description:
#   Send system information to Nagios remote server.
# 
# Example: 
#   nrdp.sh
# 
# Change log:
# 2017-08-22
#         * Improvement: Optimized to run faster.
# 
# 2015-06-30
#         * Scrash version.
# 

# Custom
URL='https://mgmt.sciemon.com/nrdp/'
TOKEN='6LasEsFov1Dag@Cotja3d1L2uvk_6w6ieAkAbByoEHasWrumUghbjiifBuAtha6u'

# Paths
PHP_CLI='/usr/bin/php'
SEND_NRDP='/opt/sciemon/xc/nrdp/clients/send_nrdp.php'

# Commands
CHECK_MYIP="/opt/sciemon/xc/check_myip.sh"
#CHECK_PING="/usr/lib/nagios/plugins/check_ping -w 10,1% -c 20,5% -H"
CHECK_SSH="/usr/lib/nagios/plugins/check_ssh -H"
CHECK_DISK="/usr/lib/nagios/plugins/check_disk -w 80 -c 90 -p"
CHECK_USER="/usr/lib/nagios/plugins/check_users -w 1 -c 2"
CHECK_PROC="/usr/lib/nagios/plugins/check_procs -w 1 -c 2 -s Z"
CHECK_LOAD="/usr/lib/nagios/plugins/check_load -w 5.0,4.0,3.0 -c 10.0,6.0,4.0"
CHECK_APT="/usr/lib/nagios/plugins/check_apt -d -t 30"
# CHECK_SWAP="/usr/lib/nagios/plugins/check_swap -w 99 -c 95"
CHECK_UPTIME='uptime'
CHECK_NTP="/usr/lib/nagios/plugins/check_ntp_peer -H"

send_nrdp_host() {
  state=$3
  output=$4
  $PHP_CLI $SEND_NRDP --url="$URL" --token="$TOKEN" --host="$HOSTNAME" --state="$state" --output="$output"
}

send_nrdp_service() {
  service=$4
  state=$5
  output=$6
  $PHP_CLI $SEND_NRDP --url="$URL" --token="$TOKEN" --host="$HOSTNAME" --service="$service" --state="$state" --output="$output"
}

# Host
{
  OUTPUT=$($CHECK_MYIP)
  RETVAL=0
  send_nrdp_host $RETVAL "$OUTPUT"
}

# Ping
# {
	# SERVICE='Ping'
	# ARG1='localhost'
	# OUTPUT=$($CHECK_PING $ARG1)
	# RETVAL=$?
  # send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
# }

# SSH
{
  SERVICE='SSH'
  ARG1='localhost'
  OUTPUT=$($CHECK_SSH $ARG1)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# Partition_Root
{
  SERVICE='Partition_Root'
  ARG1='/'
  OUTPUT=$($CHECK_DISK $ARG1)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# User
{
  SERVICE='User'
  OUTPUT=$($CHECK_USER)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# Process
{
  SERVICE='Process'
  OUTPUT=$($CHECK_PROC)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# CPU
{
  SERVICE='CPU'
  OUTPUT=$($CHECK_LOAD)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# Memory
# {
  # SERVICE='Memory'
  # OUTPUT=$($CHECK_SWAP)
  # RETVAL=$?
  # send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
# }

# APT
{
  SERVICE='APT'
  OUTPUT=$($CHECK_APT)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# NTP
{
  SERVICE='NTP'
  ARG1='localhost'
  OUTPUT=$($CHECK_NTP $ARG1)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# Uptime
{
  SERVICE='Uptime'
  OUTPUT=$($CHECK_UPTIME)
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# Interface_eth0
{
  INTERFACE='eth0'
  SERVICE="Interface_$INTERFACE"
  TMP_FILE="/tmp/nrdp_interface_$INTERFACE.tmp"
  # Packets transmited and received
  tm=$(date +'%s')
  rx=$(/sbin/ifconfig $INTERFACE | grep 'RX packets:' | awk '{print $2}' | \
       cut -d ":" -f 2)
  tx=$(/sbin/ifconfig $INTERFACE | grep 'TX packets:' | awk '{print $2}' | \
       cut -d ":" -f 2)
  # If temp file exists, use data to compute deltas
  if [ -f "$TMP_FILE" ]; then
    # Get old data
    _tm=$(cut -d " " -f 1 $TMP_FILE)
    _rx=$(cut -d " " -f 2 $TMP_FILE)
    _tx=$(cut -d " " -f 3 $TMP_FILE)
    # Get delta
    input=$((((rx - _rx) * 8) / (tm - _tm)))
    output=$((((tx - _tx) * 8) / (tm - _tm)))
  fi
  # Store data on temp file
  echo "$tm $rx $tx" > $TMP_FILE
  # Build output
  OUTPUT="$INTERFACE:UP (""$input""bps/""$output""bps):1 UP: OK | '""$INTERFACE""_in_bps'=""$input"";25000000;35000000;0;0 '""$INTERFACE""_out_bps'=""$output"";25000000;35000000;0;0"
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}

# Temperature
{
  SERVICE="Temperature"
  WARNING="55"
  CRITICAL="65"
  temp=$(awk '{printf "%3.1f", $1/1000}' /sys/class/thermal/thermal_zone0/temp)
  OUTPUT="Temperature: $temp (OK)|'temperature'=""$temp"";$WARNING;$CRITICAL;0;0"
  RETVAL=$?
  send_nrdp_service $SERVICE $RETVAL "$OUTPUT"
}
