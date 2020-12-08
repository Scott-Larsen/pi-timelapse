import boto3

from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

client = boto3.resource('sqs', region_name = 'us-east-2', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

queue = client.get_queue_by_name(QueueName = 'livestreamBool')

response = queue.send_message(MessageBody='goLive')

print(response)