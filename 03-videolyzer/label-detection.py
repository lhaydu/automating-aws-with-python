import boto3
from pathlib import Path

session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')

bucket = s3.create_bucket(Bucket='lahvideolyzervideos', CreateBucketConfiguration={'LocationConstraint': session.region_name})
pathname = 'C:\\Users\\Louise\\Downloads\\Pexels Videos 2717.mp4'
path = Path(pathname).expanduser().resolve()
bucket.upload_file(str(path), str(path.name))

rekognition_client = session.client('rekognition')
response = rekognition_client.start_label_detection(Video={'S3Object': { 'Bucket': bucket.name, 'Name': path.name}})
job_id = response['JobId']
result = rekognition_client.get_label_detection(JobId=job_id)
