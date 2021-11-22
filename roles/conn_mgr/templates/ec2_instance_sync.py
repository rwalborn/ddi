#!/usr/bin/env python
import boto3
from sets import Set
import MySQLdb
import MySQLdb.cursors
import sys
import re

# read only ops-config key
ec2_key_id = '{{ ec2_key_id }}'
ec2_access_key = '{{ ec2_access_key }}'

aws_region = '{{ aws_region }}'

db_db = '{{ db_db }}'
db_user = '{{ db_user }}'
db_passwd = '{{ db_passwd }}'
db_host = '{{ db_host }}'

ec2 = boto3.resource('ec2', aws_access_key_id=ec2_key_id, aws_secret_access_key=ec2_access_key, region_name=aws_region)
# vpcs are all collected together for us with the client view so lets not reinvent the wheel
client = boto3.client('ec2', aws_access_key_id=ec2_key_id, aws_secret_access_key=ec2_access_key, region_name=aws_region)
db = MySQLdb.connect(passwd=db_passwd, host=db_host, db=db_db, user=db_user, cursorclass=MySQLdb.cursors.DictCursor)


def get_instance_name_tag(instance):
    if instance.tags:
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value']
        return 'NoNameTag :('
    else:
        return 'NoTags :('


def get_vpc_name_tag(vpc):
    if 'Tags' in vpc:
        for tag in vpc['Tags']:
            if tag['Key'] == 'Name':
                return tag['Value']
        return 'NoNameTag :('
    else:
        return 'NoTags :('


def new_instance(instance):
    name = get_instance_name_tag(instance)
    c = db.cursor()
    c.connection.autocommit(True)
    try:
        c.execute("""INSERT INTO opstools_instance (instance_id,private_ip,public_ip,name) VALUES (%s,%s,%s,%s)""",
                  (instance.id, instance.private_ip_address, instance.public_ip_address, name))
        # instance_id is primary key so erroring here on dupe key instance is actually no big deal
        # should probably do some better checking for just that error
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown new_instance error occurred {}'.format(sys.exc_info()[0])


def update_instance(instance):
    name = get_instance_name_tag(instance)
    c = db.cursor()
    c.connection.autocommit(True)
    try:
        c.execute("""UPDATE opstools_instance SET private_ip = %s, public_ip = %s, name = %s WHERE instance_id = %s""",
                  (instance.private_ip_address, instance.public_ip_address, name, instance.id))
        # instance_id is primary key so erroring here on dupe key instance is actually no big deal
        # should probably do some better checking for just that error
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown update_instance error occurred {}'.format(sys.exc_info()[0])


def remove_instance_by_id(instance_id):
    c = db.cursor()
    c.connection.autocommit(True)
    print "Removing {}".format(instance_id)
    try:
        c.execute("DELETE FROM opstools_connection WHERE src_instance_id = '{}' OR dst_instance_id = '{}';".format(
            instance_id, instance_id))
        c.execute("DELETE FROM opstools_instance WHERE instance_id = '{}';".format(instance_id))
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown remove_instance error occurred {}'.format(sys.exc_info()[0])
        raise


def new_vpc(vpc):
    c = db.cursor()
    c.connection.autocommit(True)
    print vpc
    try:
        c.execute("""INSERT INTO opstools_vpc (vpc_id,cidr,name) VALUES (%s,%s,%s)""",
                  (vpc['VpcId'], vpc['CidrBlock'], get_vpc_name_tag(vpc)))
        # instance_id is primary key so erroring here on dupe key instance is actually no big deal
        # should probably do some better checking for just that error
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown new_vpc error occurred {}'.format(sys.exc_info()[0])


def update_vpc(vpc):
    c = db.cursor()
    c.connection.autocommit(True)
    try:
        c.execute("""UPDATE opstools_vpc SET cidr = %s, name = %s WHERE vpc_id = %s""",
                  (vpc['CidrBlock'], get_vpc_name_tag(vpc), vpc['VpcId']))
        # instance_id is primary key so erroring here on dupe key instance is actually no big deal
        # should probably do some better checking for just that error
    except MySQLdb.Error as e:
        # todo: do something with error
        print "Exception: {}\nQuery: {}\n".format(e, c._last_executed)
    except:
        print 'Unknown update_vpc error occurred {}'.format(sys.exc_info()[0])


def ec2_get_instances():
    # get all ec2 running instances from boto
    instances = ec2.instances.filter(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    print "{} Instances returned".format(len(list(instances)))
    # get all known instances from db
    c = db.cursor()
    c.execute("""SELECT * FROM opstools_instance""")
    db_instances = c.fetchall()
    # create basic sets and compare sets

    instance_set = Set()
    db_instance_set = Set()

    for row in db_instances:
        db_instance_set.add(row['instance_id'])

    for instance in instances:
        instance_set.add(instance.id)

    not_in_db = instance_set - db_instance_set
    in_both = instance_set | db_instance_set
    not_running = db_instance_set - instance_set
    print "{} instances in instance_set".format(len(instance_set))
    print "{} instances in db_instance_set".format(len(db_instance_set))
    for instance in instances:
        if instance.id in not_in_db:
            new_instance(instance)
        elif instance.id in in_both:
            update_instance(instance)
    # do some cleanup, termed instances will not be in $instances, so loop through db instances
    for instance_id in db_instance_set:
        if instance_id in not_running:
            # in database but not in running instances
            # do not delete special zones  (external records, subnets, vpcs, etc )
            pattern = re.compile("^(e-|subnet-|vpc-|i-amazonmetadata).+$")
            if not pattern.match(instance_id):
                remove_instance_by_id(instance_id)


def ec2_get_vpcs():
    # get all vpc's
    vpcs = client.describe_vpcs()

    # get all known vpcs from db
    c = db.cursor()
    c.execute("""SELECT * FROM opstools_vpc""")
    db_vpcs = c.fetchall()

    vpc_set = Set()
    db_vpc_set = Set()

    for vpc in vpcs['Vpcs']:
        vpc_set.add(vpc['VpcId'])
    for row in db_vpcs:
        db_vpc_set.add(row['vpc_id'])

    not_in_db = vpc_set - db_vpc_set
    in_both = vpc_set | db_vpc_set
    for vpc in vpcs['Vpcs']:
        if vpc['VpcId'] in not_in_db:
            new_vpc(vpc)
        elif vpc['VpcId'] in in_both:
            update_vpc(vpc)
        else:
            # in database but not in running instances
            print 'VPC not live but still in DB {}'.format(vpc['VpcId'])


if __name__ == '__main__':
    ec2_get_instances()
    ec2_get_vpcs()
