#!/usr/bin/env python

from keyring import get_password
from boto.iam.connection import IAMConnection
import lib.LoadBotoConfig as BotoConfig

from sys import exit

envs = ['dev', 'qa', 'staging', 'demo', 'prod']

for env in envs:
  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  conn = IAMConnection(aws_access_key_id=id, aws_secret_access_key=key)
  
  print(conn.get_signin_url())