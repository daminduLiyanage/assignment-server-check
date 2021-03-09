#!/usr/bin/env python
import paramiko
import botocore
import boto3
import logging
import os 

# AWS
KEY = paramiko.RSAKey.from_private_key_file("./lseg-keypair-2.pem")
INSTANCE_DNS = "ec2-18-216-216-197.us-east-2.compute.amazonaws.com"
USERNAME = "ec2-user"
AWS_ACESS_KEY_ID = 'AKIAY27W53NUD6B3LGV4'
AWS_SECRET_ACCESS_KEY = ''
PUBLIC_IP = "http://3.82.233.184/"
REGION_NAME = 'us-east-2'
BUCKET_NAME = 'lseg-assign-bucket'
MY_CONFIG = botocore.config.Config(
    region_name = REGION_NAME,
    signature_version = 'v4',
    retries = {
        'max_attempts' : 10,
        'mode' : 'standard'
    }
)

FILE_NAME = 'log'

# ------------------------------------------------------------------------
def main():
    # --------------------------------------------------------------------
    open(FILE_NAME+'.txt', 'a').close()
    s3 = boto3.resource(
                's3', 
                aws_access_key_id=AWS_ACESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name = REGION_NAME
                )
    s3.meta.client.upload_file(FILE_NAME+".txt", BUCKET_NAME, FILE_NAME+".txt")
    # Created empty log file in S3
# end main method
