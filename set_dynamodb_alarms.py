#!/usr/bin/env python

from keyring import get_password
from boto.ec2.cloudwatch import connect_to_region as connect_to_cw_region
from boto.ec2.cloudwatch import MetricAlarm
from boto.dynamodb import connect_to_region as connect_to_db_region
from time import sleep
import lib.LoadBotoConfig as BotoConfig

region = 'us-east-1'
check = 'ThrottledRequests'
operations = ['PutItem', 'Query', 'GetItem', 'BatchGetItem']
topics = {
              'demo' : 'arn:aws:sns:us-east-1:NNNNNNNNNNNNNNNN:XXXXXXXXXXXXXXXXX',
              'qa' : 'arn:aws:sns:us-east-1:NNNNNNNNNNNNNNNN:XXXXXXXXXXXXXXXXX',
              'prod' : 'arn:aws:sns:us-east-1:NNNNNNNNNNNNNNNN:XXXXXXXXXXXXXXXXX'
            }

for env in topics:
  topic = topics[env]

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  db = connect_to_db_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  cw = connect_to_cw_region(region, aws_access_key_id=id, aws_secret_access_key=key)

  tables = db.list_tables()

  for table in tables:
      for operation in operations:
          alarm_name = table + '-ThrottledRequests-' + operation
          try:
              alarm = MetricAlarm(name=alarm_name,
                                  comparison='>=',
                                  threshold=3,
                                  period=300,
                                  evaluation_periods=1,
                                  statistic='Sum',
                                  alarm_actions=[topic],
                                  namespace='AWS/DynamoDB',
                                  metric=check,
                                  dimensions={"Operation":operation, "TableName":table})
              cw.create_alarm(alarm)
              print("Created {0} in {2} {1}".format(alarm_name, env.upper(), region))
          except Exception:
              print("COULD NOT CREATE {0}".format(alarm_name))
          sleep(0.15)
