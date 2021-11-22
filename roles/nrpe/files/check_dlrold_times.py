#!/usr/bin/env python

import requests
import datetime
import numpy
import sys
from time import sleep


from optparse import OptionParser

parser = OptionParser()

parser.add_option('-H', '--host', dest='host', default='doubledowncasino.com',
				help="HOSTNAME, depending on function. Default: doubledowncasino.com")
parser.add_option('-p', '--path', dest='path', default='/order/index',
				help="HOSTNAME, depending on function. Default: doubledowncasino.com")
parser.add_option('-w', '--warning', type='int', dest='warning',
				help="Average response time in mililiseconds to warn on")
parser.add_option('-c', '--critical', type='int', dest='critical',
				help="Average response time in milliseconds to crit on")
parser.add_option('-r', '--runtime', type='int', dest='run', default=20,
				help="Run time for the check loop (checks once a second). Default: 20")

(options, args) = parser.parse_args()


warning = datetime.timedelta(milliseconds=options.warning)
critical = datetime.timedelta(milliseconds=options.critical)

url = "http://" + options.host + options.path

runtime = datetime.timedelta(seconds=options.run)
request_time_list = []
request_list = []

start = datetime.datetime.now()
while runtime >= datetime.datetime.now() - start:
	r = requests.post(url)
	request_list.append(r)
	request_time_list.append(r.elapsed)
	sleep(1)

avg_req = sum(request_time_list, datetime.timedelta(0)) / len(request_time_list)

count = 0
for i in request_list:
	try:
		dict = i.json()
		break
	except ValueError:
		count += 1

if count >= ( len(request_list) / 2 ):
	print "CRITICAL: Too many bad responses!"
	sys.exit(2)

if avg_req >= warning and avg_req < critical:
	print "WARNING: AVG Dealer to Casino Response time is " + str(avg_req) + " | avgresp=" + str(avg_req)
	sys.exit(1)
if avg_req >= critical:
	print "CRITICAL: AVG Dealer to Casino Response time is " + str(avg_req) + " | avgresp=" + str(avg_req)
	sys.exit(2)
if avg_req < warning:
	print "OK: AVG Dealer to Casino Response time is " + str(avg_req) + " | avgresp=" + str(avg_req)
	sys.exit(0)

