import json
import urllib
import boto3

def start_label_detection(bucket, key):
    rekognition_client = boto3.client('rekognition')
    response = rekognition_client.start_label_detection(
        Video={'S3Object': {
            'Bucket': bucket,
            'Name': key
            }
        })

    print(response)
    return
    #job_id = response['JobId']
    #result = rekognition_client.get_label_detection(JobId=job_id)

def start_processing_video(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        start_label_detection(bucket_name, key )

    # response = rekognition_client.start_label_detection(Video={'S3Object': { 'Bucket': bucket.name, 'Name': path.name}})
    # job_id = response['JobId']
    # result = rekognition_client.get_label_detection(JobId=job_id)

    return
