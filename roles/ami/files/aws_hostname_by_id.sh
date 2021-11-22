#!/bin/bash

# chkconfig: 2345 11 99
# description: change hostname
#              needs ec2:DescribeTags in 'AmazonEC2ReadOnlyAccess' policy

case $1 in
start)
  AZ=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
  REGION=${AZ%?}
  ID=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
  IDSTR=`echo $ID | sed 's/^i-//'`
  CURRENTNAME=`hostname --short`

  # only makes change when instance-id is not in current hostname
  if [[ $CURRENTNAME != *$IDSTR* ]]
  then
    # can't always assume Name is Tag[0], query instead
    TAG=`aws ec2 describe-tags --region $REGION --filter "Name=resource-id,Values=$ID" --query "Tags[?Key=='Name'].Value" --output text`
    if [ -z "$TAG" ] || [ "$TAG" == 'null' ]
    then
      echo 'unexpected TAG value, maybe the instance does not have a role'
      exit 1
    fi
    # only use the string before the 1st space, if any
    TAG1=`echo $TAG | awk '{print $1}'`
    NEWNAME=$TAG1-$IDSTR
    sed -i "s/^HOSTNAME=.*$/HOSTNAME=$NEWNAME/" /etc/sysconfig/network
    hostname $NEWNAME
  fi
  ;;
stop)
  ;;
*)
  $0 start
esac
