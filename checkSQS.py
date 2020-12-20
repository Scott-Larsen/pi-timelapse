import subprocess
import boto3
import os
import subprocess

from time import sleep

from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, SQS_URL, STREAM_TOKEN

import boto3
client = boto3.client('sqs', region_name='us-east-2',
                    aws_access_key_id=AWS_ACCESS_KEY_ID, 
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

QueueUrl = SQS_URL

LIVESTREAM_COMMAND = "raspivid -o - -t 0 -vf -hf -fps 24 -b 4500000 -rot 180 | ffmpeg -re -an -f s16le -i /dev/zero -i - -vcodec copy -acodec aac -ab 384k -g 17 -strict experimental -f flv -t 300 rtmp://live-jfk.twitch.tv/app/"

response = client.receive_message(
    QueueUrl=QueueUrl,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0
)

savedResponse = response
if 'Messages' in savedResponse:
    message = savedResponse['Messages'][0]
    if message['Body'] == 'goLive':
        print("Going Live!")
        os.system(LIVESTREAM_COMMAND + STREAM_TOKEN)
        # subprocess.run([LIVESTREAM_COMMAND + STREAM_TOKEN])
        # subprocess.run(["raspivid", -o - -t 0 -vf -hf -fps 24 -b 4500000 -rot 180 | ffmpeg -re -an -f s16le -i /dev/zero -i - -vcodec copy -acodec aac -ab 384k -g 17 -strict experimental -f flv -t 10 rtmp://live-jfk.twitch.tv/app/live_615939706_hg8xASdvmVMMIN8R5GbhAfGf2EL44y"])
        # sleep(300)

    receipt_handle = message['ReceiptHandle']

    # Delete message
    client.delete_message(
        QueueUrl=QueueUrl,
        ReceiptHandle=receipt_handle
    )



# # client = boto3.resource('sqs', region_name = 'us-east-2', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

# # QueueURL = SQS_URL

# # Create SQS client
# sqs = boto3.client('sqs', region_name = 'us-east-2', aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

# # queue_url = SQS_URL # 'SQS_QUEUE_URL'

# # # Receive message from SQS queue
# # response = sqs.receive_message(
# #     QueueUrl=queue_url,
# #     AttributeNames=[
# #         'SentTimestamp'
# #     ],
# #     MaxNumberOfMessages=1,
# #     MessageAttributeNames=[
# #         'All'
# #     ],
# #     VisibilityTimeout=0,
# #     WaitTimeSeconds=0
# # )

# # print(response)
# # message = response['Messages'][0]
# # receipt_handle = message['ReceiptHandle']

# # # Delete received message from queue
# # sqs.delete_message(
# #     QueueUrl=queue_url,
# #     ReceiptHandle=receipt_handle
# # )
# # print(f'Received and deleted message: {message}') # % message)




# response = sqs.receive_message(
#     QueueUrl=SQS_URL,
#     AttributeNames=[
#         'SentTimestamp'
#     ],
#     MaxNumberOfMessages=1,
#     MessageAttributeNames=[
#         'All'
#     ],
#     VisibilityTimeout=0,
#     WaitTimeSeconds=0
# )




# sqs = boto3.client('sqs') 
# queue = sqs.get_queue_url(QueueName='queue_name')
# # # get_queue_url will return a dict e.g.
# # # {'QueueUrl':'......'}
# # # You cannot mix dict and string in print. Use the handy string formatter
# # # will fix the problem   
# # print "Queue info : {}".format(queue)

# # responses = sqs.send_message(QueueUrl= queue['QueueUrl'], MessageBody='Test')
# # # send_message() response will return dictionary  
# # print "Message send response : {} ".format(response) 





# # queue = client.get_queue_by_name(QueueName = 'livestreamBool')

# # response = queue.send_message(MessageBody='goLive')
