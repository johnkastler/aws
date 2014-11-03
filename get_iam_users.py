#!/usr/bin/env python

from keyring import get_password
from boto import connect_iam
import lib.LoadBotoConfig as BotoConfig
from sys import exit

envs = BotoConfig.envs

for each in envs:
  env = each.split(':')[0]
  region = each.split(':')[1:]

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  conn = connect_iam(aws_access_key_id=id, aws_secret_access_key=key)

  print(env)

  data = conn.get_all_users()
  for user in data.list_users_result.users:
      print(user.user_name)

  print("")
