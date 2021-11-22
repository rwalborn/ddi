#!/usr/bin/env python

"""Check disk await.

Run iostat on a device and check await.  Warn is above specified threshold.
"""


import commands
import os
import re
import stat
import sys
from optparse import OptionParser

# Globals
IOSTAT_BIN = '/usr/bin/iostat'

def get_vg_disks(vg_name):
  """Do some pvdisplay magic to get disks in a volume group.

  Args:
    None
  
  Returns:
    devices: list of all block devices found
  """
  
  
  PVDIS_CMD = "sudo /usr/sbin/pvdisplay -C --separator '  ' -o pv_name,vg_name | awk '/" + vg_name + "/ { print $1 }'"


  # Variable setup.
  pvdis_out = commands.getstatusoutput(PVDIS_CMD)
  if pvdis_out[0] != 0:
	  print "Error getting devices from volume group"
	  sys.exit(-1)

  devices = pvdis_out[1].split('\n')

  return devices


def output_and_exit(messages, perfdata, code=0):
  """Output messages and exit with correct return code.

  Args:
    messages: list of all status messages
    code: integer representing our exit code

  Returns:
    None
  """
  for message in messages:
    print message + ", ",

  for perf in perfdata:
    print perf,

  sys.exit(code)


def main():
  """Check await on specified block device."""
  # Setup our flags.
  flags = OptionParser()
  flags.add_option('-w', '--warn', dest='warning', type='int',
                   default=15, help='Warning threshold', metavar='INT')
  flags.add_option('-c', '--crit', dest='critical', type='int',
                   default=20, help='Critical threshold', metavar='INT')
  flags.add_option('-d', '--dev', dest='device', type='string',
                   default='ALL', help='Device to check', metavar='DEV')
  (opts, dummy) = flags.parse_args()

  # Assign options.
  dev = opts.device

  all_devices = get_vg_disks(dev)

  # Default our warning levels and messages.
  warn = False
  crit = False
  messages = []
  perfdata = [' | ']


  # Loop through all our devices and set any alerts levels and messages.
  for device in all_devices:
    # Grab device await
    iostat_data = commands.getstatusoutput('%s -x %s' % (IOSTAT_BIN, device))

    # This is a literal, based on iostat output
    stats_list = iostat_data[1].split('\n')[-2].split()
    dev_await = stats_list[9]
    perfdata.append('%s=%s, ' % (device, dev_await))

    # Check our critical threshold.
    if float(dev_await) >= opts.critical:
      messages.append('Device await on %s critical: %sms' %
                      (device, dev_await))
      crit = True
    # Check our warning threshold.
    elif float(dev_await) >= opts.warning:
      messages.append('Device await on %s warning: %sms' %
                      (device, dev_await))
      warn = True
    # Say things are fine.
    else:
      messages.append('Device await on %s within range: %sms' %
                      (device, dev_await))

  # Exit, outputting our messages, based on the most extreme level.
  if crit:
    output_and_exit(messages, perfdata, 2)
  elif warn:
    output_and_exit(messages, perfdata,  1)
  else:
    output_and_exit(messages, perfdata)


if __name__ == '__main__':
  main()
