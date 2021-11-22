# base on https://github.com/awslabs/dynamodb-backup-scheduler
# modified to use cloudwatch event

# TODO: clarify backup and retention logic within 2 days

from __future__ import print_function
from datetime import date, datetime, timedelta
import json
import boto3
import time
from botocore.exceptions import ClientError
import os

backupName = 'dynamodbbackup_v0.9'


def lambda_handler(event, context):
    try:
        ddbRegion = os.environ['AWS_DEFAULT_REGION']
        ddb = boto3.client('dynamodb', region_name=ddbRegion)
        ddbTable = event['table']
        daysToLookBackup = event['retention']
        daysToLookBackupL = daysToLookBackup-1

        # create backup
        ddb.create_backup(TableName=ddbTable, BackupName=backupName)
        print('Backup has been taken successfully for table:', ddbTable)

        # check recent backup
        timenow = datetime.now()
        # upper bound is exclusive, backups created on the same day are not listed
        upperDate = timenow
        lowerDate = timenow - timedelta(days=daysToLookBackupL)
        begin = upperDate.strftime('%m/%d/%Y %H:%M:%S')
        end = lowerDate.strftime('%m/%d/%Y %H:%M:%S')

        responseLatest = ddb.list_backups(TableName=ddbTable, TimeRangeLowerBound=datetime(lowerDate.year, lowerDate.month, lowerDate.day), TimeRangeUpperBound=datetime(upperDate.year, upperDate.month, upperDate.day))
        latestBackupCount = len(responseLatest['BackupSummaries'])
        print('Total backup count between %s and %s is %d' % (begin, end, latestBackupCount))

        deleteupperDate = upperDate - timedelta(days=daysToLookBackup)
        # TimeRangeLowerBound is the release of Amazon DynamoDB Backup and Restore - Nov 29, 2017
        response = ddb.list_backups(TableName=ddbTable, TimeRangeLowerBound=datetime(2017, 11, 29), TimeRangeUpperBound=datetime(deleteupperDate.year, deleteupperDate.month, deleteupperDate.day))

        # check whether latest backup count is more than two before removing the old backup
        if latestBackupCount >= 2:
            if 'LastEvaluatedBackupArn' in response:
                lastEvalBackupArn = response['LastEvaluatedBackupArn']
            else:
                lastEvalBackupArn = ''

            while (lastEvalBackupArn != ''):
                for record in response['BackupSummaries']:
                    backupArn = record['BackupArn']
                    ddb.delete_backup(BackupArn=backupArn)
                    print(backupName, 'has deleted this backup:', backupArn)
        else:
            print ('Recent backup does not meet the deletion criteria')

    except ClientError as e:
        print(e)

    except ValueError as ve:
        print('error:', ve)

    except Exception as ex:
        print(ex)
