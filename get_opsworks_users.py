#!/usr/bin/env python

"""
pulls some basic data for an opsworks user as imported from IAM
"""

from keyring import get_password
import lib.LoadBotoConfig as BotoConfig
import lib.AWSConn as AWSConn
from boto import connect_opsworks
from sys import exit

envs = BotoConfig.envs

for each in envs:
  env = each.split(':')[0]
  region = each.split(':')[1:]
  
  id = BotoConfig.config.get(env, 'aws_access_key_id')
  key = get_password(BotoConfig.config.get(env, 'keyring'), id)
  account = BotoConfig.config.get(env, 'accountid')

  conn = connect_opsworks(aws_access_key_id=id, aws_secret_access_key=key)
  profiles = conn.describe_user_profiles().get('UserProfiles')
  
  for profile in profiles:
    name = profile.get('SshUsername')    
    selfman = profile.get('AllowSelfManagement')
    sshkey = profile.get('SshPublicKey')
    if sshkey:
      sshkey = 'True'
    else:
      sshkey = 'False'
    print("  - {4} {5}: User: {0}, Self-Manage: {1}, SSH Key: {2}".format(name, selfman, sshkey, account, env, region))
  
  print("")