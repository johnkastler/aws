#!/usr/bin/env python

username = 'FilePicker'
role_name = 'FilePicker'
policy_name = 'policygen-FilePicker-201407171355'
policy_document = '''{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1405619384000",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:ListBucketVersions",
        "s3:ListMultipartUploadParts",
        "s3:PutObject"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}'''

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
    print(conn.create_role(role_name))
    print(conn.put_role_policy(role_name, policy_name, policy_document))
    conn.create_user(username, path='/')
    print(conn.create_access_key(user_name=username))
    print("Created {0} in {1} {2}".format(username, env, region))
    conn.put_user_policy(username, policy_name, policy_document)
  except Exception:
    if conn.get_user(user_name=username):
      print("{0} already exists in {1} {2}, skipping".format(username, env, region))
    else:
      print("Error")