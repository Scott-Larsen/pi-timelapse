import boto3

from config import (
    AWS_REGION_NAME,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    SQS_QUEUE_NAME,
)

client = boto3.resource(
    "sqs",
    region_name=AWS_REGION_NAME,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

queue = client.get_queue_by_name(QueueName=SQS_QUEUE_NAME)

response = queue.send_message(MessageBody="goLive")

print(response)