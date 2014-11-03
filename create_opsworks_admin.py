#!/usr/bin/env python

"""
PASSWORD POLICY

- Minimum Password Length: 8
- Require at least one uppercase letter
- Require at least one lowercase letter
- Require at least one number
- Require at least one non-alphanumeric character

"""

username = ''
password = ''
sshkey = ''

from keyring import get_password
from boto import connect_iam, connect_opsworks
import lib.LoadBotoConfig as BotoConfig

envs = BotoConfig.envs

for each in envs:
  env = each.split(':')[0]
  region = each.split(':')[1:]

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)
  group_name = BotoConfig.config.get(env, 'admingroup')

  conniam = connect_iam(aws_access_key_id=id, aws_secret_access_key=key)
  connops = connect_opsworks(aws_access_key_id=id, aws_secret_access_key=key)

  try:
    conniam.create_user(username, path='/')
    conniam.create_login_profile(username, password)
    conniam.add_user_to_group(group_name, username)
    print("Created {0} in {1} {2}".format(username, env, region))
  except Exception:
    if conniam.get_user(user_name=username):
      print("{0} already exists in {1} {2}, skipping".format(username, env, region))
    else:
      print("Error")

  user_response = conniam.get_user(username).get('get_user_response')
  user_result = user_response.get('get_user_result')
  user = user_result.get('user')
  arn = user.get('arn')

  try:
    connops.create_user_profile(arn, ssh_username=username, ssh_public_key=sshkey, allow_self_management=True)
    print("Added {0} to OpsWorks in {1} {2}".format(username, env, region))
  except Exception:
    connops.update_user_profile(arn, ssh_username=username, ssh_public_key=sshkey, allow_self_management=True)
