#!/usr/bin/env python

username = ''
password = ''

from keyring import get_password
from boto import connect_iam
import lib.LoadBotoConfig as BotoConfig
from sys import exit

envs = BotoConfig.envs

group_name = 'dynamodb_admins'
group_policy_name = 'policygen-dynamodbadmins-201407161001'
group_policy = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1405519246000",
      "Effect": "Allow",
      "Action": [
        "dynamodb:*"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}'''

for each in envs:
  env = each.split(':')[0]
  region = each.split(':')[1:]

  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)

  conn = connect_iam(aws_access_key_id=id, aws_secret_access_key=key)

  try:
    conn.create_group(group_name, path='/')
    conn.put_group_policy(group_name, group_policy_name, group_policy)
  except:
    pass
  
  try:
    conn.create_user(username, path='/')
    print(conn.create_login_profile(username, password))
    print("Created {0} in {1} {2}".format(username, env, region))

  except Exception:
    if conn.get_user(user_name=username):
      print("{0} already exists in {1} {2}, skipping".format(username, env, region))
    else:
      print("Error")
  
  try:
    conn.add_user_to_group(group_name, username)
  except:
    pass