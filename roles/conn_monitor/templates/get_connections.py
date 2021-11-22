#!/usr/bin/python -w
import subprocess
import re
import requests
import boto3
import json
from sys import getsizeof

# variables
# (read only sqs key for specific sqs queue ) from ansible-vault
aws_key_id = '{{ sqs_key_id }}'
aws_access_key = '{{ sqs_access_key }}'
sqs_queue = 'connection_monitoring'
aws_region = 'us-east-1'


def error(msg):
    # do some other error stuff... email ?
    print "ERROR: {}".format(msg)


def get_connections(idata):
    ss = subprocess.Popen("ss -4 -n", stdout=subprocess.PIPE, shell=True)
    (connections, err) = ss.communicate()
    status = ss.wait()

    # find ip addresses and ports separated by whitespace
    regex = r"(\d+\.\d+\.\d+\.\d+):(\d+)\s+(\d+\.\d+\.\d+\.\d+):(\d+)"
    matches = re.findall(regex, connections)
    well_known_ports = [22, 80, 443, 5672, 8080, 9339, 11210, 27017, 60006]
    results = []
    if matches:
        for match in matches:
            # try to determine source/dest flow direction based on port info.  assume larger port number is 'client'
            # or if it is in well known port list
            if int(match[1]) in well_known_ports:
                # source port is really dest port, flip pairs
                src_ip = match[2]
                src_port = match[3]
                dst_ip = match[0]
                dst_port = match[1]
            elif int(match[3]) in well_known_ports:
                # dest port is well known, trust this
                src_ip = match[0]
                src_port = match[1]
                dst_ip = match[2]
                dst_port = match[3]
            elif int(match[3]) > int(match[1]):
                # if neither port is in well_known, use bigger port as client
                src_ip = match[2]
                src_port = match[3]
                dst_ip = match[0]
                dst_port = match[1]
            else:
                # assume match[1] is client because it is either bigger or equal
                # equal no way to tell, just use match[0] as client
                src_ip = match[0]
                src_port = match[1]
                dst_ip = match[2]
                dst_port = match[3]
            # print "SRC: {0} SRCPRT: {1} DST: {2} DSTPRT: {3}".format(src_ip, src_port, dst_ip, dst_port)
            results.append({'src_ip': src_ip, 'src_port': int(src_port), 'dst_ip': dst_ip, 'dst_port': int(dst_port)})

        return results
    else:
        error("No regex matches found in connection output")


# retrieve instance-id from ec2 metadata
def get_instance_data():
    data = {}
    url = 'http://169.254.169.254/latest/meta-data/'
    attributes = ['instance-id', 'local-ipv4', 'public-ipv4']
    for attr in attributes:
        r = requests.get("{0}{1}".format(url,attr))
        # public ip may not be set, so ignore 404's
        if r.status_code == 404:
            print 'No attribute found for {0}'.format(attr)
        elif r.status_code != 200:
            error("Can not retrieve instance id, status code {0}".format(r.status_code))
        else:
            data[attr] = r.text
    return data


def queue_connections(instance_data, connections):
    # add to sqs queue
    sqs = boto3.resource('sqs', aws_access_key_id=aws_key_id, aws_secret_access_key=aws_access_key, region_name=aws_region)
    queue = sqs.get_queue_by_name(QueueName=sqs_queue)
    data = {'instance_data': instance_data, 'connections': connections}
    # messagebody must be a string, so lets make it json
    response = queue.send_message(MessageBody=json.dumps(data))
    print('Message queued: {0}'.format(response.get('MessageId')))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


if __name__ == '__main__':
    instance_data = get_instance_data()
    connections = get_connections(instance_data)
    # max size of sqs message is 256,000
    if getsizeof(json.dumps(connections)) > 240000:
        # too many connections (bytes) for one message, lets get chunks of 2500 max lines
        for connects in chunks(connections, 2500):
            queue_connections(instance_data, connects)
    else:
        queue_connections(instance_data, connections)
