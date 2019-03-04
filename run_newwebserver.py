#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
#from consolemenu import
#from consolemenu.items import

#menu = ConsoleMenu("Assignment automation", "Subtitle")

#menu_item = MenuItem("Menu Item")

#function_item = FunctionItem(create())

#def create():
#create a security group
ec2 = boto3.client('ec2')

response = ec2.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    response = ec2.create_security_group(GroupName='Assignment Group',
                                         Description='used for assignment',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)


ec2 = boto3.resource('ec2')
instance = ec2.create_instances(
    ImageId='ami-047bb4163c506cd98',
    MinCount=1,
    MaxCount=1,
    SecurityGroupIds=[security_group_id],
    InstanceType='t2.micro')
print (instance[0].id)