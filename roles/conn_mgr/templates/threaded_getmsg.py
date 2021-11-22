#!/usr/bin/env python
import boto3
import threading
import json
import MySQLdb
import MySQLdb.cursors
import random
import sys
import ipaddress
import time
import re

# credentials filled in from ansible playbook secrets.yml

# read only ops-config key
ec2_key_id = '{{ ec2_key_id }}'
ec2_access_key = '{{ ec2_access_key }}'

# sqs queue manager key
sqs_key_id = '{{ sqs_key_id }}'
sqs_access_key = '{{ sqs_access_key }}'

# variables
sqs_queue = '{{ sqs_queue }}'
aws_region = '{{ aws_region }}'
db_db = '{{ db_db }}'
db_user = '{{ db_user }}'
db_passwd = '{{ db_passwd }}'
db_host = '{{ db_host }}'


num_threads = 10

# connections
sqs = boto3.resource('sqs', aws_access_key_id=sqs_key_id, aws_secret_access_key=sqs_access_key, region_name=aws_region)
ec2 = boto3.resource('ec2', aws_access_key_id=ec2_key_id, aws_secret_access_key=ec2_access_key, region_name=aws_region)


def make_ipnetwork(cidr):
    try:
        ipnetwork = ipaddress.ip_network(u'{}'.format(cidr))
        return ipnetwork
    except ValueError as e:
        if e.message != "{} has host bits set".format(cidr):
            raise
        else:
            # try again with strict = False when its a host bit error
            ipnetwork = ipaddress.ip_network(u'{}'.format(cidr), False)
            return ipnetwork


def get_instance_by_ip_mysql(ip, db):
    c = db.cursor()
    c.connection.autocommit(True)
    c.execute("""SELECT * FROM opstools_instance WHERE private_ip = %s OR public_ip = %s""", (ip, ip))
    try:
        row = c.fetchone()
        if row:
            return row
        else:
            return 'NoInstance'
    except MySQLdb.Error as e:
        print e
    except:
        print 'Unknown get_instance_by_ip_mysql error occurred {}'.format(sys.exc_info()[0])


def get_instance_by_id_mysql(i_id, db):
    c = db.cursor()
    c.connection.autocommit(True)
    c.execute("""SELECT * FROM opstools_instance WHERE instance_id = %s""", (i_id, ))
    try:
        row = c.fetchone()
        return row
    except MySQLdb.Error as e:
        print e
    except:
        print 'Unknown get_instance_by_ip_mysql error occurred {}'.format(sys.exc_info()[0])


def get_vpcs_mysql(db):
    c = db.cursor()
    c.connection.autocommit(True)
    try:
        c.execute("""SELECT * FROM opstools_vpc""",)
        rows = c.fetchall()
        return rows
    except MySQLdb.Error as e:
        print e
    except:
        print "Unknown get_vpcs_mysql error occurred {}".format(sys.exc_info()[0])


def get_subnets_mysql(db):
    c = db.cursor()
    c.connection.autocommit(True)
    c.execute("""SELECT * FROM opstools_subnet""",)
    try:
        rows = c.fetchall()
        return rows
    except MySQLdb.Error as e:
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown get_subnets_mysql error occurred {}'.format(sys.exc_info()[0])


def instance_exists_mysql(id, db):
    c = db.cursor()
    c.connection.autocommit(True)
    try:
        c.execute("""SELECT * FROM opstools_instance WHERE instance_id = %s""", (id, ))
        row = c.fetchone()
        if row:
            return True
        else:
            return False
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown new_instance error occurred {}'.format(sys.exc_info()[0])


def find_instance_id_mysql(ip, db):
    instance = get_instance_by_ip_mysql(ip, db)
    if instance == 'NoInstance':
        # do some ip range checking here to see if it is an instance that has just spun up or ip space
        # outside of known ranges
        # e-External  is a fake instance w/ 0.0.0.0
        vpcs = get_vpcs_mysql(db)
        ipnet = make_ipnetwork('{}/32'.format(ip))
        for vpc in vpcs:
            vpcnet = make_ipnetwork(vpc['cidr'])
            if ipnet.overlaps(vpcnet):
                # ip is inside this vpc subnet
                data = {'instance-id': vpc['vpc_id'], 'private-ipv4': vpcnet.network_address,
                        'public-ipv4': 'NULL', 'name': vpc['name']}
                new_instance(data, db)
                return vpc['vpc_id']
        subnets = get_subnets_mysql(db)
        for subnet in subnets:
            snet = make_ipnetwork(subnet['cidr'])
            if ipnet.overlaps(snet):
                snet_id = 'subnet-{}'.format(subnet['name'])
                data = {'instance-id': snet_id, 'private-ipv4': '127.0.0.1', 'public-ipv4': snet.network_address,
                        'name': subnet['name']}
                new_instance(data, db)
                return snet_id
        # if we get to here it doesnt' match any known subnets or vpc's so it must be external
        return "e-External"
    else:
        return instance['instance_id']


def new_instance(idata, db):
    c = db.cursor()
    c.connection.autocommit(True)
    idata = check_idata(idata)
    if not instance_exists_mysql(idata['instance-id'], db):
        try:
            c.execute("""INSERT INTO opstools_instance (instance_id,private_ip,public_ip,name) VALUES (%s,%s,%s,%s)""",
                  (idata['instance-id'], idata['private-ipv4'], idata['public-ipv4'], idata['name']))
            # instance_id is primary key so erroring here on dupe key instance is actually no big deal
            # should probably do some better checking for just that error
        except MySQLdb.Error as e:
            # todo: do something with error
            print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
        except:
            print 'Unknown new_instance error occurred {}'.format(sys.exc_info()[0])


def get_db_connections(instance_data, db):
    connections = []
    c = db.cursor()
    c.connection.autocommit(True)
    try:
        c.execute("""SELECT * FROM opstools_connection WHERE (src_instance_id = %s OR dst_instance_id = %s)""",
                  (instance_data['instance-id'], instance_data['instance-id'],))
        if c.rowcount < 1:
            # no connections at all, assume first run
            new_instance(instance_data,db)
        else:
            connections = c.fetchall()
        return connections
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown get_db_connections error occurred {}'.format(sys.exc_info()[0])


def check_idata(data):
    if 'instance_data' in data:
        idata = data['instance_data']
    else:
        idata = data
    if not 'private-ipv4' in idata:
        idata['private-ipv4'] = '127.0.0.1'
    if not 'public-ipv4' in idata:
        idata['public-ipv4'] = 'NULL'
    if not 'name' in idata:
        idata['name'] = 'NULL'
    return idata


def db_connection_exist(db_connections, connection):
    for db_conn in db_connections:
        if db_conn['src_ip'] == connection['src_ip'] and db_conn['dst_ip'] == connection['dst_ip'] \
                and db_conn['dst_port'] == connection['dst_port']:
            # we have existing database connection so ignore this one
            # print "Con: {} Found, skipping".format(connection)
            return True
        elif db_conn['dst_ip'] == connection['dst_ip'] and db_conn['dst_port'] == connection['dst_port'] \
                and db_conn['src_instance_id'] == 'e-External':
            return True
    # no matches found in looping
    # print "Con: {} Not Found, looking up".format(connection)
    return False


def insert_connections(connections, db):
    c = db.cursor()
    c.connection.autocommit(True)

    for con in connections:
        try:
            c.execute("""INSERT INTO opstools_connection (src_ip,dst_ip,dst_port,dst_instance_id,src_instance_id) VALUES
                (%s,%s,%s,%s,%s)""", (con['src_ip'], con['dst_ip'], con['dst_port'], con['dst_instance_id'],
                                      con['src_instance_id']))
            # instance_id is primary key so erroring here on dupe key instance is actually no big deal
            # should probably do some better checking for just that error
        except MySQLdb.Error as e:
            # todo: do something with error
            print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
        except:
            print 'Unknown insert_connections error occurred {}'.format(sys.exc_info()[0])
            return False
    return True


def already_seen(cons, con):
    for c in cons:
        if c['src_ip'] == con['src_ip'] and c['dst_ip'] == con['dst_ip'] and c['dst_port'] == con['dst_port'] and \
                c['src_instance_id'] == con['src_instance_id'] and c['dst_instance_id'] == con['dst_instance_id']:
            return True
    return False


def process_message(message, db, t_id):
    starttime = time.time()
    data = json.loads(message.body)
    numlines = len(data['connections'])
    data['instance_data'] = check_idata(data)
    # each message is a collection of connections recorded by a specific instance
    # grab all known connections for that instance for comparison
    db_connections = get_db_connections(data['instance_data'], db)
    newcons = []
    for connection in data['connections']:
        if db_connection_exist(db_connections, connection):
            continue
        src_instance_id = ''
        dst_instance_id = ''
        # if the source or dest is 127.0.0.1 set the appropriate instance-id to self
        if connection['src_ip'] == '127.0.0.1':
            src_instance_id = data['instance_data']['instance-id']
        if connection['dst_ip'] == '127.0.0.1':
            dst_instance_id = data['instance_data']['instance-id']
        if ((connection['src_ip'] == data['instance_data']['private-ipv4']) or
                (connection['src_ip'] == data['instance_data']['public-ipv4'])):
            # connection is sourced from reporting instance
            src_instance_id = data['instance_data']['instance-id']
            # only lookup dst_instance_id if it's not already set
            if dst_instance_id == '':
                dst_instance_id = find_instance_id_mysql(connection['dst_ip'], db)
        elif ((connection['dst_ip'] == data['instance_data']['private-ipv4']) or
                (connection['dst_ip'] == data['instance_data']['public-ipv4'])):
            dst_instance_id = data['instance_data']['instance-id']
            # only lookup src_instance_id if it's not already set
            if src_instance_id == '':
                src_instance_id = find_instance_id_mysql(connection['src_ip'], db)
        else:
            # if it isn't set by now.. let's try looking for it by connection ip
            if src_instance_id == '':
                src_instance_id = find_instance_id_mysql(connection['src_ip'], db)
            if dst_instance_id == '':
                dst_instance_id = find_instance_id_mysql(connection['dst_ip'], db)

        # if dst_instance_id == 'e-External':
        #    connection['dst_ip'] = '0.0.0.0'
        # do not track sources for inbound connections but still track for outbound
        if src_instance_id == 'e-External':
            dst_instance = get_instance_by_id_mysql(dst_instance_id, db)
            pattern = re.compile("^(REPLACEMENT2-SFS|LB|SFS).+$")
            # replace src_ip only on nodes that are supposed to have public traffic, leave the rest
            if pattern.match(dst_instance['name']):
                connection['src_ip'] = '0.0.0.0'
        # prepare connection hash for adding to newcons
        newcon = {'src_ip': connection['src_ip'], 'dst_ip': connection['dst_ip'],
                   'dst_port': connection['dst_port'], 'src_instance_id': src_instance_id,
                   'dst_instance_id': dst_instance_id}

        # make sure connection does not exist in db table or in the insert queue variable
        #    (after we have detected & set instance ids

        if not db_connection_exist(db_connections, connection):
            # check if the new connection is already in the queue table, sometimes a new one comes in multiple times
            if not already_seen(newcons, newcon):
                newcons.append(newcon)
    # only delete the message from the queue if it was successfully inserted
    if insert_connections(newcons, db):
        message.delete()
    endtime = time.time()
    time_taken = endtime - starttime
    print "Thread-{} Process Message completed {} lines in {} seconds".format(t_id, numlines, time_taken)
    if time_taken > 20.0:
        print 'This thread was very slow, here are the connections contained inside for debug'
        print data['connections']



def poll_messages(t_id):
    starttime = time.time()
    db = MySQLdb.connect(passwd=db_passwd, db=db_db, host=db_host, user=db_user, cursorclass=MySQLdb.cursors.DictCursor)
    queue = sqs.get_queue_by_name(QueueName=sqs_queue)
    for message in queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=10):
        process_message(message, db, t_id)
    db.close()
    endtime = time.time()
    print "Thread-{} complete, took {} seconds".format(t_id, endtime - starttime)
    # kick off another thread, stagger timing a bit so all threads are not fighting each other
    threading.Timer(random.randint(0, 15), poll_messages(t_id)).start()


if __name__ == '__main__':
    threads = []
    for x in range(1, num_threads):
        t = threading.Thread(target=poll_messages, args=(x,))
        threads.append(t)
        t.start()
