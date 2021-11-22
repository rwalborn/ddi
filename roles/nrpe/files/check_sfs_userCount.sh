#!/bin/sh
# The following log file logs once a minute lines of the following format:
# COUNT, DELTA, TIMESTAMP
LOGFILE=/home/SFS_PRO_1.6.6/Server/logs/userCount.log

# The most recently recorded timestamp.
TIMESTAMP=`tail -1 $LOGFILE |sed -e "s/..*, //"`

# The most recently recorded user count
USERCOUNT=`tail -1 $LOGFILE |sed -e "s/,..*//"`

# The timestamps stored in userCount.log are all in seconds since midnight in GMT. This gives us the same measurement.
NOW=$((`date +%s`%86400))

#Check to make sure the last timestamp in userCount.log isn't off by more than 2 minutes in either direction.
DIFF=$(($NOW-$TIMESTAMP))
if (( $DIFF > 180 )); then
  exit 2
fi
if (( $DIFF < -180 )); then
  exit 2
fi

echo "`date +'%F %R'` $1 | UserCount=$USERCOUNT"
