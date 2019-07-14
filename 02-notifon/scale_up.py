# coding: utf-8
import boto3
session = boto3.Session(profile_name='pythonAutomation')
as_client = session.client('autoscaling')
as_client.describe_auto_scaling_groups()
as_client.describe_policies()

as_client.execute_policy(AutoScalingGroupName='Notifon Example Group', PolicyName='Scale Down')
as_client.execute_policy(AutoScalingGroupName='Notifon Example Group', PolicyName='Scale Up')
#create Lambda
#handleCloudWatchExample w/ runtime of Python 3.6
# role create new role handleCloudWatchEventExampleRole
# policy .... simple microservice permissions
# just have it print the event; no triggers ... cloudwatch will capture the output
# create Event - rule for Auto Scaling for Event Type "EC2 instance launch successful"
# target is the Lambda function
# target creates a trigger for Lambda
