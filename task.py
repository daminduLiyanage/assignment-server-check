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
AWS_SECRET_ACCESS_KEY = '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'
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

# Log messages
AT_START = " -- NEW RUN -- "
SERVER_STATUS = "SERVER STATUS: "
SERVER_SSH_CHECK_OK = "SERVER SERVICE CHECK DONE"

# Email 
# Note: Email addresses must be verified through AWS
SEND_TO = ['damindu7@gmail.com',]
EMAIL_FROM = 'damindu7@gmail.com'
EMAIL_SUBJECT = 'Assignment server failure'
EMAIL_TEXT = 'Error occured with ec2 lseg assignment Apache server.'
EMAIL_HTML = '<p>Error occured with ec2 lseg assignment Apache server. Please refer log</p>'

# File Names
LOG_FILE_NAME = 'log.txt'
FILE_FROM_BUCKET = 'download.txt'
FILE_TO_BUCKET = 'upload.txt'

# ------------------------------------------------------------------------
def conn():
    # --------------------------------------------------------------------
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return sshClient
# end conn method

# ------------------------------------------------------------------------
def start_logger():
    # --------------------------------------------------------------------
    """
    logging configuration
    :return:
    """
    logging.basicConfig(
        filename=LOG_FILE_NAME,
        format='%(asctime)s %(message)s',
        filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.info("task.sh Initiated...")
    return logger
# end start_logger method

# ------------------------------------------------------------------------
def main():
    # --------------------------------------------------------------------
    try:
        logger = start_logger()
        logger.info(AT_START)
        sshClient = conn()
        sshClient.connect(hostname=INSTANCE_DNS, username=USERNAME, pkey=KEY)
        # 1
        cmd = "systemctl is-active --quiet httpd  || sudo systemctl start httpd"
        # Check if httpd runs start if not
        stdin, stdout, stderr = sshClient.exec_command(cmd)
        output = stdout.read()
        logger.info(SERVER_SSH_CHECK_OK+output.decode("utf-8"))
        sshClient.close() 
        # 2 
        cmd = "curl -s -o /dev/null -w \"%{http_code}\" "+PUBLIC_IP
        # Check for status 200
        output = os.popen(cmd).read()
        logger.info(SERVER_STATUS+output)
        # 3
        s3 = boto3.resource(
            's3', 
            aws_access_key_id=AWS_ACESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name = REGION_NAME
            )
        s3.meta.client.download_file(BUCKET_NAME, LOG_FILE_NAME, FILE_FROM_BUCKET)
        filenames = [FILE_FROM_BUCKET,LOG_FILE_NAME]
        with open(FILE_TO_BUCKET, 'w') as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
        # downloaded file appended to log file beggining
        s3.meta.client.upload_file(FILE_TO_BUCKET, BUCKET_NAME, LOG_FILE_NAME)
        os.remove(FILE_FROM_BUCKET)
        os.remove(FILE_TO_BUCKET)
    except Exception as e:
        # 4
        logger.warning(e)
        ses = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=MY_CONFIG
            )
        # The email details 
        response = ses.send_email(
            Source=EMAIL_FROM,
            Destination={
                'ToAddresses': SEND_TO,
                    },
            Message={
                'Subject': {
                    'Data': EMAIL_SUBJECT,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': EMAIL_TEXT,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': EMAIL_HTML,
                        'Charset': 'UTF-8'
                    }
                }
            },
            ReplyToAddresses=[
            ],
        )
        logger.warning(response)
# end main method