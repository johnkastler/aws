#!/usr/bin/env python

from keyring import get_password
from boto.cloudsearch2 import connect_to_region
from time import sleep
import lib.LoadBotoConfig as BotoConfig

env = 'dev'
region = 'us-east-1'

id = BotoConfig.config.get(env, 'aws_access_key_id')
key = get_password(BotoConfig.config.get(env, 'keyring'), id)

#print(id)
#print(key)
#exit(0)
try:
  conn = connect_to_region(region, aws_access_key_id=id, aws_secret_access_key=key)
except:
  print('error')
domains = conn.describe_domains()['DescribeDomainsResponse']
domains = domains['DescribeDomainsResult']
domains = domains['DomainStatusList']
print(domains)