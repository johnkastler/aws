#!/usr/bin/env python

email_contacts = [
                  '',
                  '',
                  '',
                  ''
                ]
topics = {
              #'arn:aws:sns:us-east-1::dynamodb' : 'qa',
              'arn:aws:sns:us-east-1::demo-dynamodb' : 'demo',
              'arn:aws:sns:us-east-1::staging-dynamodb' : 'staging',
              'arn:aws:sns:us-east-1::dynamodb-throttledRequests' : 'prod',
              'arn:aws:sns:eu-west-1::dynamodb' : 'prod',
              'arn:aws:sns:ap-southeast-2::dynamodb' : 'prod'
            }
sns_protocol = 'email'  
app = 'alp'
service = 'dynamodb'
check = 'ThrottledRequests'
operations =  [
                'PutItem',
                'DeleteItem',
                'UpdateItem',
                'GetItem',
                'BatchGetItem',
                'Scan',
                'Query'
              ]


from keyring import get_password
from boto.ec2.cloudwatch import connect_to_region as connect_to_cw_region
from boto.ec2.cloudwatch import MetricAlarm
from boto.dynamodb import connect_to_region as connect_to_db_region
from boto.sns import connect_to_region as connect_to_sns_region
from time import sleep
import lib.LoadBotoConfig as BotoConfig

for topic in topics:
  env = topics[topic]
  region = topic.split(':')[3]
  print(env)
  print(region)

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  db = connect_to_db_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  cw = connect_to_cw_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  sns = connect_to_sns_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  
  existing_subs = []
  subs = sns.get_all_subscriptions_by_topic(topic)
  subs = subs.get('ListSubscriptionsByTopicResponse')
  subs = subs.get('ListSubscriptionsByTopicResult')
  subs = subs.get('Subscriptions')
  
  for sub in subs:
    sub = sub.get('Endpoint')
    existing_subs.append(sub)

  for endpoint in email_contacts:
    if endpoint not in existing_subs:
      print("subscribing {0} to {1} {2}".format(endpoint, env, region))
      sns.subscribe(topic, sns_protocol, endpoint)
 
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
          except Exception, e:
              print("COULD NOT CREATE {0}".format(alarm_name))
          sleep(0.1)