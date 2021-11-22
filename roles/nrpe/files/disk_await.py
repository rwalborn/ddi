#!/usr/bin/python

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


def get_block_devs():
  """Parse /etc/mtab for valid block devices.

  Args:
    None
  
  Returns:
    devices: list of all block devices found
  """
  # Variable setup.
  devices = []

  # If we don't have read access to /etc/mtab, we need to warn and bail.
  try:
    mtab_fh = open('/etc/mtab', 'r')
  except IOError:
    print 'Could not open /etc/mtab.'
    sys.exit(3)

  # Look for any lines that start with '/dev/'.
  device_pattern = re.compile('^/dev/')
  for line in mtab_fh:
    if device_pattern.match(line):
      # Append the first 'word' found in a matching line.
      devices.append(line.split()[0])

  return devices


def output_and_exit(messages, code=0):
  """Output messages and exit with correct return code.

  Args:
    messages: list of all status messages
    code: integer representing our exit code

  Returns:
    None
  """
  for message in messages:
    print message
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

  # If we're not checking 'ALL,' make sure our device exists and is a valid
  # block device.
  if not dev is 'ALL':
    try:
      dev_st_mode = os.lstat(dev)[0]
      # Bail if the device specified isn't a block device.
      if not stat.S_ISBLK(dev_st_mode):
        print '%s is not a valid block device.' % dev
        sys.exit(3)
      # We'll need to be able to iterate over this later.
      all_devices = [dev]
    except OSError:
      # Bail if the device isn't found at all.
      print '%s not found.' % dev
      sys.exit(3)
  else:
    all_devices = get_block_devs()

  # Default our warning levels and messages.
  warn = False
  crit = False
  messages = []

  # Loop through all our devices and set any alerts levels and messages.
  for device in all_devices:
    # Grab device await
    iostat_data = commands.getstatusoutput('%s -x %s' % (IOSTAT_BIN, device))

    # This is a literal, based on iostat output
    stats_list = iostat_data[1].split('\n')[-2].split()
    dev_await = stats_list[9]

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
    output_and_exit(messages, 2)
  elif warn:
    output_and_exit(messages, 1)
  else:
    output_and_exit(messages)


if __name__ == '__main__':
  main()
