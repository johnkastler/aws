#!/usr/bin/env python

from yaml import safe_load
from time import sleep
from keyring import get_password
from boto.dynamodb2 import connect_to_region
import lib.LoadBotoConfig as BotoConfig
import traceback
from sys import exit

tables_conf = open('set_dynamodb_throughput.yaml')
tables = safe_load(tables_conf)
tables_conf.close()

topics = {
  'arn:aws:sns:us-east-1::dynamodb' : 'qa',
  #'arn:aws:sns:us-east-1::demo-dynamodb' : 'demo',
  #'arn:aws:sns:us-east-1::staging-dynamodb' : 'staging',
  #'arn:aws:sns:us-east-1::dynamodb-throttledRequests' : 'prod',
  #'arn:aws:sns:eu-west-1::dynamodb' : 'prod',
  #'arn:aws:sns:ap-southeast-2::dynamodb' : 'prod'
}

for topic, env in topics.iteritems():
  
  region = topic.split(':')[3]

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  db = connect_to_region(region, aws_access_key_id=id, aws_secret_access_key=key)
  
  print(env, region)
  print('')
  
  for table, values in tables.iteritems():
    
    desiredReadCapacity = values['read']
    desiredWriteCapacity = values['write']

    table_description = db.describe_table(table)

    tableinfo = db.describe_table(table)['Table']
    throughputinfo = tableinfo['ProvisionedThroughput']
    
    try:
      
      GlobalSecondaryIndexes = table_description.get('Table')
      GlobalSecondaryIndexes = GlobalSecondaryIndexes['GlobalSecondaryIndexes']
    
    except Exception:
      
      GlobalSecondaryIndexes = False
      print('crap1')
      print traceback.format_exc()
    
    if GlobalSecondaryIndexes:

      for GlobalSecondaryIndex in GlobalSecondaryIndexes:

        GSIReadCapacityUnits = GlobalSecondaryIndex['ProvisionedThroughput']
        GSIReadCapacityUnits = GSIReadCapacityUnits['ReadCapacityUnits']
        GSIWriteCapacityUnits = GlobalSecondaryIndex['ProvisionedThroughput']
        GSIWriteCapacityUnits = GSIWriteCapacityUnits['WriteCapacityUnits']

        if GSIReadCapacityUnits >= desiredReadCapacity and GSIWriteCapacityUnits >= desiredWriteCapacity:
          continue
         
        if GSIReadCapacityUnits * 2 < desiredReadCapacity:
          new_ReadCapacityUnits = GSIReadCapacityUnits * 2
        else:
          new_ReadCapacityUnits = desiredReadCapacity

        if GSIWriteCapacityUnits * 2 < desiredWriteCapacity:
          new_WriteCapacityUnits = GSIWriteCapacityUnits * 2
        else:
            new_WriteCapacityUnits = desiredWriteCapacity
         
        GlobalSecondaryIndexName = GlobalSecondaryIndex['IndexName']

        try:

          db.update_table(
            table_name=table,
            global_secondary_index_updates=[
              {
                "Update": {
                  "IndexName": GlobalSecondaryIndexName,
                  "ProvisionedThroughput": {
                    "ReadCapacityUnits": new_ReadCapacityUnits,
                    "WriteCapacityUnits" : new_WriteCapacityUnits
                  }
                }
              }
            ]
          )
          print('updating {0} in {1} {2}'.format(GlobalSecondaryIndexName, table.upper(), region, env.upper()))

          sleep(1)
      
        except Exception:
          print('crap2')
          print(traceback.format_exc())
          pass
   
    ReadCapacityUnits = throughputinfo['ReadCapacityUnits']
    WriteCapacityUnits = throughputinfo['WriteCapacityUnits']

    if ReadCapacityUnits >= desiredReadCapacity and WriteCapacityUnits >= desiredWriteCapacity:
      continue
          
    if ReadCapacityUnits * 2 < desiredReadCapacity:
      new_ReadCapacityUnits = ReadCapacityUnits * 2
    else:
      new_ReadCapacityUnits = desiredReadCapacity

    if WriteCapacityUnits * 2 < desiredWriteCapacity:
      new_WriteCapacityUnits = WriteCapacityUnits * 2
    else:
      new_WriteCapacityUnits = desiredWriteCapacity
    
    if ReadCapacityUnits == desiredReadCapacity and WriteCapacityUnits == desiredWriteCapacity:
      continue
    
    try:
    
      db.update_table(
        table_name=table,
        provisioned_throughput=
        {
          "ReadCapacityUnits": new_ReadCapacityUnits,
          "WriteCapacityUnits" : new_WriteCapacityUnits
        }
      )
      
      print('updating {0} in {1} {2}'.format(table.upper(), region, env.upper()))
      print(' - new Read limit is {0} and new Write limit is {1}'.format(new_ReadCapacityUnits, new_WriteCapacityUnits))
      print('')
      
      sleep(4)
      
    except Exception:
      print('crap3')
      print(traceback.format_exc())
      pass