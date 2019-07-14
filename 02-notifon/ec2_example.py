# coding: utf-8

import boto3

session = boto3.Session(profile_name='pythonAutomation')

ec2 = session.resource('ec2')
key_name = 'python_automation_key'
key_path = key_name + '.pem'
print(key_path)
key = ec2.create_key_pair(KeyName=key_name)
key.key_material
with open(key_path, 'w') as key_file:
    key_file.write(key.key_material)

# doesn't work on Windows
# run under Ubuntu on Windows after changing permissions
import os, stat
os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
### working steps
ec2.images.filter(Owners=['amazon'])
list(ec2.images.filter(Owners=['amazon']))
len(list(ec2.images.filter(Owners=['amazon'])))

# actual steps needed to create ec2 InstanceType
ami_name = 'amzn-ami-hvm-2018.03.0.20180508-x86_64-gp2'
filters = [{'Name': 'name', 'Values': [ami_name]}]

list(ec2.images.filter(Owners=['amazon'], Filters=filters))

img = ec2.Image('ami-922914f7')

# First find the AMI (console)
# Get the AMI id
# Get name of the AMI id
# Make a filter based on name... while work across regions
# image id, instance type, get
instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)

inst = instances[0]
inst.wait_until_running()

inst.reload()
inst.public_dns_name

inst.security_groups
#Look up security group
#authorize incoming connections from our puclic IP address on port 22

sg=ec2.SecurityGroup(inst.security_groups[0]['GroupId'])
sg.authorize_ingress(IpPermissions=[{'FromPort': 22, 'ToPort': 22, 'IpProtocol': 'TCP', 'IpRanges': [{'CidrIp': '69.250.57.37/32'}]}])
sg.authorize_ingress(IpPermissions=[{'FromPort': 80, 'ToPort': 80, 'IpProtocol': 'TCP', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}])

# stress tool ... sudo yum -y install stress
# stress -c 1 -t 600&
