#!/bin/bash

logline=`tail -n1 /home/SFS_PRO_1.6.6/Server/logs/rgsRequestTimeLog.log`

usage() {
cat << EOF
usage: $0 options

This checks the latest logline from rgsRequestTimeLog

OPTIONS:
 -h	Show this
 -w	warning
 -c	critical
 -a	action
EOF
}

result=`echo $logline | awk -F\, '{ print "total="$1", errors="$2 ", mean="$3 ", 50th%="$4 ", 90th%="$5 ", max="$6}'`

echo "OK: This script is only for graphing | $result"

