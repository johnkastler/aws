#!/usr/bin/env python

topics = {
              'arn:aws:sns:us-east-1::dynamodb' : 'qa',
              'arn:aws:sns:us-east-1::demo-dynamodb' : 'demo',
              'arn:aws:sns:us-east-1::staging-dynamodb' : 'staging',
              'arn:aws:sns:us-east-1::dynamodb-throttledRequests' : 'prod',
              'arn:aws:sns:eu-west-1::dynamodb' : 'prod',
              'arn:aws:sns:ap-southeast-2::dynamodb' : 'prod'
            }

from keyring import get_password
from boto.ec2.cloudwatch import connect_to_region as connect_to_cw_region
import lib.LoadBotoConfig as BotoConfig

for topic in topics:
  env = topics[topic]
  region = topic.split(':')[3]
  print("{0} - {1}".format(env, region))
  print("")
  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  cw = connect_to_cw_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  
  alarms = cw.describe_alarms(state_value='ALARM')
  if alarms:
    for alarm in alarms:
      alarm = str(alarm)
      alarm = alarm.split(':')[1]
      alarm = alarm.split('[')[0]
      print("  - {0}".format(alarm))
  else:
    print("  - No alarms")
  print("")