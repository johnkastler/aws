#!/usr/bin/env python

topics = {
              'arn:aws:sns:us-east-1::dynamodb' : 'qa',
              #'arn:aws:sns:us-east-1::alp-demo-dynamodb' : 'demo',
              #'arn:aws:sns:us-east-1::alp-staging-dynamodb' : 'staging',
              #'arn:aws:sns:us-east-1::dynamodb-throttledRequests' : 'prod',
              #'arn:aws:sns:eu-west-1::dynamodb' : 'prod',
              #'arn:aws:sns:ap-southeast-2::dynamodb' : 'prod'
            }
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
from boto.dynamodb2 import connect_to_region as connect_to_db_region
import lib.LoadBotoConfig as BotoConfig
from sys import exit
import datetime

starttime = datetime.datetime.now() - datetime.timedelta(seconds=600)
endtime = datetime.datetime.now()

for topic in topics:
  env = topics[topic]
  region = topic.split(':')[3]
  print("{0} - {1}".format(env, region))
  print("")
  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  cw = connect_to_cw_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  db = connect_to_db_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  
  tables = db.list_tables()['TableNames']
  for table in tables:
    
    metrics = cw.list_metrics(dimensions={ 'TableName' : table }, namespace='AWS/DynamoDB')
    print(table, metrics)
    print('')
    continue
    for metric in metrics:
      metric = str(metric).split(':')[1]
      print(metric)
      print('')
      continue
      for operation in operations:
        metric_stats =  cw.get_metric_statistics(
          60,
          starttime,
          endtime,
          metric,
          'AWS/DynamoDB',
          'Sum',
          dimensions={ 'TableName' : table, 'Operation' : operation }
        )
        
        if len(metric_stats) > 0:
          print(table, operation, metric)
          print(metric_stats)
          print('')