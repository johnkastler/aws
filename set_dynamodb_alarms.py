#!/usr/bin/env python

from keyring import get_password
from boto.ec2.cloudwatch import connect_to_region as connect_to_cw_region
from boto.ec2.cloudwatch import MetricAlarm
from boto.dynamodb import connect_to_region as connect_to_db_region
from time import sleep
import lib.LoadBotoConfig as BotoConfig

app = 'XXXXXXXXXX'
envs = ['dev', 'qa', 'staging', 'demo', 'prod']
region = 'us-east-1'
check = 'ThrottledRequests'
operations = ['PutItem', 'Query', 'GetItem', 'BatchGetItem']
topic = 'dynamodb'

for env in envs:
  accountid = BotoConfig.config.get(env, 'accountid')
  topic_name = 'arn:aws:sns:' + region + ':' + accountid + ':' + app + '-' + env + '-' + topic
  
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
                                  alarm_actions=[topic_name],
                                  namespace='AWS/DynamoDB',
                                  metric=check,
                                  dimensions={"Operation":operation, "TableName":table})
              cw.create_alarm(alarm)
              print("Created {0} in {2} {1}".format(alarm_name, env.upper(), region))
          except Exception:
              print("COULD NOT CREATE {0}".format(alarm_name))
          sleep(0.25)
