#!/usr/bin/env python

username = 'CircleCI'

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

  try:
    conn.create_user(username, path='/')
    print(conn.create_access_key(user_name=username))
    print("Created {0} in {1} {2}".format(username, env, region))
    policy = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1407167363000",
      "Effect": "Allow",
      "Action": [
        "opsworks:CreateDeployment"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Sid": "Stmt1407167379000",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::hostedops-resources/heatseeker/current"
      ]
    }
  ]
}'''
    conn.put_user_policy(username, 'policygen-CircleCI-201407101222', policy)
  except Exception:
    if conn.get_user(user_name=username):
      print("{0} already exists in {1} {2}, skipping".format(username, env, region))
    else:
      print("Error")