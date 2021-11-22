#!/bin/bash

PID=`ps -ef | grep [j]ava | grep [s]martfox | awk '{ print $2 }'`
/usr/lib64/nagios/plugins/extra/check_jstat.sh -p $PID
return_code=$?

exit $return_code