#!/usr/bin/env python

from keyring import get_password
from boto.s3 import connect_to_region
import lib.LoadBotoConfig as BotoConfig
from sys import exit
from yaml import safe_load

buckets_conf = open('create_s3_buckets.yaml')
buckets = safe_load(buckets_conf)
buckets_conf.close()

envs = BotoConfig.envs



for bucket in buckets:
  policy = bucket[0]
  #permissions = bucket['permissions']
  #print(type(bucket))
  print(policy)
  #print(permissions)
  exit(0)

for each in envs:
  #env = each.split(':')[0]
  env = 'dev'
  #region = each.split(':')[1:]
  region = 'us-east-1'

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  db = connect_to_region(region, aws_access_key_id=id, aws_secret_access_key=key)

  conn.list_grants()
  exit(0)
  for bucket in buckets:
    create_bucket(bucket_name, headers=None, location='', policy=None)
    add_user_grant(permission, user_id, recursive=False, headers=None, display_name=None)