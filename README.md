# Automating AWS with Python

Repository for "Automating AWS with Python" course

## 01-webotron
Webotron is a script that will sync a local directory to an S3 bucket

### Features
Webotron currently has the following features:
- List buckets
- List contents of a bucket
- Create and set up a bucket
- Sync directory tree to bucket
- Set AWS profile with --profile=<profilename>
- Output bucket name from sync command
- Set Up Domain
- Publish to CDN with CloudFront and SSL Support


## 02-notifon

Notifon is a project to notify Slack users of changes to your AWS account using
CloudWatch Events

### Features

Notifon currently has the following features:
- Send notifications to Slack when CloudWatch events happen


#### Notes
Serverless framework - uses CloudFormation to automate deployment and config
of servlerless, such as Lambda.
>>> sls create -t aws-ptyhon3 -n notifon-notifier
>>> serverless create --template aws-python3 --name notifon-notifier
