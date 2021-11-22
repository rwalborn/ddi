#!/bin/bash

curl -s http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key > /tmp/my-key
if [ $? -eq 0 ] ; then
  if ! grep -q -f /tmp/my-key /root/.ssh/authorized_keys ; then
    cat /tmp/my-key >> /root/.ssh/authorized_keys
  fi
  chmod 600 /root/.ssh/authorized_keys
  rm /tmp/my-key
fi
