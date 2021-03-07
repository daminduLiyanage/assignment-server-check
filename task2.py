#!/usr/bin/env python
import paramiko
from scp import SCPClient
import botocore
import boto3
import os 
import shutil
import logging
 
# AWS
KEY = paramiko.RSAKey.from_private_key_file("./lseg-keypair-2.pem")
INSTANCE_DNS = "ec2-18-216-216-197.us-east-2.compute.amazonaws.com"
USERNAME = "ec2-user"
AWS_ACESS_KEY_ID = 'AKIAY27W53NUD6B3LGV4'
AWS_SECRET_ACCESS_KEY = '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'
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

# File Names
TEMP_FOLDER_NAME = "tmp"
REMOTE_HTML_PATH = "/var/www/html/"
REMOTE_LOG_PATH = "/var/log/httpd/"
ARCHIVE_NAME = "compressed"
ARCHIVE_FORMAT = "zip"
SERVER_CONTENT = "server_content"
SERVER_LOGS = "server_logs"
REMOTE_ARCHIVE_NAME='compressed.zip'
LOG_FILE_NAME="task2_log.txt"

# Email 
# Note: Email addresses must be verified through AWS
SEND_TO = ['damindu7@gmail.com',]
EMAIL_FROM = 'damindu7@gmail.com'
EMAIL_SUBJECT = 'Assignment server failure'
EMAIL_TEXT = 'Error occured with ec2 lseg assignment Apache server.'
EMAIL_HTML = '<p>Error occured with ec2 lseg assignment Apache server. Process: task2.  Please refer log.</p>'

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
        # 1
        logger = start_logger()
        sshClient = conn()
        sshClient.connect(hostname=INSTANCE_DNS, username=USERNAME, pkey=KEY)
        sftp = sshClient.open_sftp()
        os.mkdir(TEMP_FOLDER_NAME)
        os.mkdir(TEMP_FOLDER_NAME+"/"+SERVER_CONTENT)
        os.mkdir(TEMP_FOLDER_NAME+"/"+SERVER_LOGS)
        for eachFileName in sftp.listdir(REMOTE_HTML_PATH):
            sftp.get(REMOTE_HTML_PATH+eachFileName, "./"+TEMP_FOLDER_NAME+"/"+SERVER_CONTENT+"/"+eachFileName) 
        for eachFileName in sftp.listdir(REMOTE_LOG_PATH):
            sftp.get(REMOTE_LOG_PATH+eachFileName, "./"+TEMP_FOLDER_NAME+"/"+SERVER_LOGS+"/"+eachFileName) 
        # Downloaded files from server
        sftp.close()
        # 2 
        shutil.make_archive(ARCHIVE_NAME, ARCHIVE_FORMAT, TEMP_FOLDER_NAME)
        shutil.rmtree(TEMP_FOLDER_NAME)
        # 3
        s3 = boto3.resource(
                's3', 
                aws_access_key_id=AWS_ACESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name = REGION_NAME
                )
        s3.meta.client.upload_file(ARCHIVE_NAME+".zip", BUCKET_NAME, ARCHIVE_NAME+".zip")
        os.remove(ARCHIVE_NAME+".zip")
    except:
        # 4
        ses = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            config=MY_CONFIG
            )
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
# end main method