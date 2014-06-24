#!/usr/bin/env python

from keyring import get_password
from boto.sns import connect_to_region as connect_to_sns_region
from boto.ec2.cloudwatch import connect_to_region as connect_to_cw_region
from boto.dynamodb import connect_to_region as connect_to_db_region
import lib.LoadBotoConfig as BotoConfig

env = "qa"
region = 'us-east-1'

id =  BotoConfig.config.get(env, 'aws_access_key_id')
key = get_password(BotoConfig.config.get(env, 'keyring'), id)

db = connect_to_db_region(region, aws_access_key_id=id, aws_secret_access_key=key)
sns = connect_to_sns_region(region, aws_access_key_id=id, aws_secret_access_key=key)
cw = connect_to_cw_region(region, aws_access_key_id=id, aws_secret_access_key=key)

topics = sns.get_all_topics()
topic = topics[u'ListTopicsResponse']['ListTopicsResult']['Topics'][0]['TopicArn']

tables = db.list_tables()

for table in tables:
  counter = 0
  metric_length = len(cw.list_metrics(dimensions={'TableName':table}, metric_name="ThrottledRequests"))
  while counter <= metric_length:
    try:
      metrics = cw.list_metrics(dimensions={'TableName':table}, metric_name="ThrottledRequests")[counter]
      alarm_name = 'ThrottledRequests_' + str(counter) + '_' + table
      metrics.create_alarm(name=alarm_name, comparison='>=',
                        threshold=1,
                        period=300,
                        evaluation_periods=2,
                        statistic='Average',
                        alarm_actions=[topic])
      print("applied alarm to {0}".format(table))
    except Exception:
      pass
    counter = counter + 1
