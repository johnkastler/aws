#!/usr/bin/env python

from keyring import get_password
from boto.ec2 import connect_to_region
import lib.LoadBotoConfig as BotoConfig
from sys import exit

id = BotoConfig.config.get('hosted', 'aws_access_key_id')
key = get_password(BotoConfig.config.get('hosted', 'keyring'), id)

conn = connect_to_region('us-east-1', aws_access_key_id=id, aws_secret_access_key=key)

volumes = conn.get_all_volumes()

for volume in volumes:
  volume = str(volume)
  volume = volume.split(':')[1]
  
  abc = conn.get_all_volume_status(volume_ids=volume)
  print(abc)
  
  print("boo")
  print()