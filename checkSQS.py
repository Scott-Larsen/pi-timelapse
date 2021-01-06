import boto3
import os
from time import sleep

from config import AWS_REGION_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SQS_URL

import boto3

client = boto3.client(
    "sqs",
    region_name=AWS_REGION_NAME,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

QueueUrl = SQS_URL


def checkSQSforGoLiveCommand():
    response = client.receive_message(
        QueueUrl=QueueUrl,
        AttributeNames=["SentTimestamp"],
        MaxNumberOfMessages=1,
        MessageAttributeNames=["All"],
        VisibilityTimeout=0,
        WaitTimeSeconds=0,
    )

    savedResponse = response
    if "Messages" in savedResponse:
        message = savedResponse["Messages"][0]
        if message["Body"] == "goLive":

            receipt_handle = message["ReceiptHandle"]

            # Delete message
            client.delete_message(QueueUrl=QueueUrl, ReceiptHandle=receipt_handle)

            return True
