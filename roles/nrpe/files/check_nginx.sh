#/bin/bash

PROCNUM=`ps -ef | grep ngin[x] | wc -l`

if [ $PROCNUM -eq "0" ]; then
	echo "CRITICAL: Nginx not running"
	exit 2
else
	echo "OK: Nginx running"
	exit 0
fi

