#!/usr/bin/env python
# For example:

import sys
import re
import json
from optparse import OptionParser
import pprint
sys.path.append('.')
import rightscale_connection
import time

parser = OptionParser()
parser.add_option('-r', '--rightscript', dest='rightscript', help="Name of the rightscript you want to run")
parser.add_option('-a', '--server_array', dest='server_array', help="The path to the server array you want to run it on")
parser.add_option('-i', '--input', dest='inputs', help="Comma-delimited list of the inputs you want to pass in (e.g. param1=value,param2=value)")

(options, args) = parser.parse_args()

rs_connection = rightscale_connection.rightscale_connection()
rs_connection.authenticate()
rightscript = rs_connection.get_by_path("right_scripts:"+options.rightscript)

inputs = rs_connection.stringify_kvp10_inputs(options.inputs)
inputs += "&right_script_href="+rightscript["links"]["self"]
timeout = 600 # if it ain't done in 10 minutes...

server_array = rs_connection.get_by_path(options.server_array)
status_array = {}
http_error_count = 0
for instance in server_array.values():
  status_array[instance["name"]] = {}
  status_array[instance["name"]]["status"] = "unknown"
  instance = rs_connection.unfuck_links(instance)
  if instance["state"] == "operational":
    sys.stdout.write("Running "+options.rightscript+" on instance "+instance["name"]+"\n")
    response = rs_connection.json_relative_post(instance["links"]["self"]+"/run_executable"+inputs)
    if response.status_code not in [201, 202]:
      sys.stderr.write("Call to run "+options.rightscript+" on instance "+instance["name"]+" returned HTTP "+str(response.status_code)+"\n")
      status_array[instance["name"]]["status"] = "HTTP " + str(response.status_code)
      http_error_count += 1
    else:
      sys.stdout.write(options.rightscript+" on instance " + instance["name"]+" execution status available at " + rs_connection.api_url + response.headers['location']+"\n")
      status_array[instance["name"]]["location"] = response.headers["location"]
start_time = int(time.time())
while ((int(time.time()) - start_time) < timeout ):
#  handle 500s, yo
  completion_matrix = {"completed" : 0, "failed" : 0, "error" : http_error_count}
  for server in status_array:
    status = "unknown"
    if "location" in status_array[server]:
      response = rs_connection.json_relative_request(status_array[server]["location"])
      status = re.sub(":..*", "", response["summary"])
    if status not in completion_matrix.keys():
      completion_matrix[status] = 0
    completion_matrix[status] += 1
    sys.stdout.write(server+": "+status+"\n")
  sys.stdout.write("Successes: "+str(completion_matrix["completed"]) + " Errors: "+str(completion_matrix["error"]) + " Failures: "+str(completion_matrix["failed"])+"\n")
  if completion_matrix["completed"] +  completion_matrix["error"] + completion_matrix["failed"] == len(server_array):
    sys.stdout.write("Done.\n")
    sys.exit(completion_matrix["error"] + completion_matrix["failed"])
