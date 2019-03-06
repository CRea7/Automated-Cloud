#!/usr/bin/env python3
import sys
import boto3
import time
import subprocess
from botocore.exceptions import ClientError

def main():
    #security_group_id = create_security()
    instance_id = create_instance()
    #print('please wait 60 seconds')
    #time.sleep(60)
    #print('sleep over')
    #bucket_name = create_bucket()
    #put_image_bucket(bucket_name)

def create_security():

    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')


    try:
        response = ec2.create_security_group(GroupName='Assignment Group',
                                            Description='used for assignment',
                                            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created :' + str(security_group_id))

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
    #print('Ingress Successfully Set %s' % data)
    except ClientError as e:
        print(e)
    return security_group_id

#creates instance using security group that was previously created and my key pair
def create_instance():

    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-047bb4163c506cd98',
        MinCount=1,
        MaxCount=1,
        UserData = """ #!/bin/bash
                       sudo yum update -y
                       sudo yum install -y httpd
                       sudo chkconfig httpd on
                       sudo /etc/init.d/httpd start
                       """,#installs apache web server thing
        SecurityGroupIds=['sg-08c2e007a2f47781e'],
        KeyName = 'CRea_KeyPair',   #key pair located in dcuments
        InstanceType='t2.micro')
    print (instance[0].id)
    while not instance[0].public_ip_address:
        try:
            instance[0].reload()
            if instance[0].public_ip_address:
                # Public IP address is available
                public_ip = instance[0].public_ip_address
                print(instance[0].public_ip_address)

        except Exception as e:
            return instance[0].public_ip_address

def create_bucket():
    s3 = boto3.resource("s3")
    for bucket_name in sys.argv[1:]:
        try:
            response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
            print (response)
        except Exception as error:
            print (error)
    return bucket_name

def put_image_bucket(bucket_name):
    s3 = boto3.client('s3')
    bucket = bucket_name
    file_name = './icon.png'
    key_name = 'icon.png'
    s3.upload_file(file_name, bucket, key_name)

def ssh_onto_server():
    ssh_command = "ssh -tt -o StrictHostKeyChecking=no -i" + key_location[: -1] + "ec2-user@"\
                  +instance_dns + " sudo ls -a"
    subprocess.run(ssh_command, check=True, shell=True)

# ssh -t -i ~/Documents/CRea_KeyPair.pem ec2-user@52.19.206.250
if __name__ == '__main__':
    main()
