#!/usr/bin/env python3
import sys
import boto3
import time
import subprocess
import check_webserver
from botocore.exceptions import ClientError

def main():
    #security_group_id = create_security()
    bucket_name = create_bucket()
    bucket_name = bucket_name.lower()
    image_url = put_image_bucket(bucket_name)
    print(image_url)
    instance_ip = create_instance(image_url)
    print('please wait 60 seconds')
    time.sleep(120)
    print('sleep over')
    ssh_onto_server(instance_ip)

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
def create_instance(image_url):

    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-047bb4163c506cd98',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=['sg-08c2e007a2f47781e'],
        KeyName = 'CRea_KeyPair',   #key pair located in dcuments
        InstanceType='t2.micro',
        UserData = """ #!/bin/bash
                       sudo yum update -y
                       sudo yum install -y httpd
                       sudo yum install python3
                       sudo chkconfig httpd on
                       sudo /etc/init.d/httpd start
                       echo "<h2>Test page</h2>Instance ID: " > /var/www/html/index.html
                       curl --silent http://169.254.169.254/latest/meta-data/instance-id/ >> /var/www/html/index.html
                       curl --silent http://169.254.169.254/latest/meta-data/placement/availability-zone/ >> /var/www/html/index.html
                       echo "<br>IP address: " >> /var/www/html/index.html
                       curl --silent http://169.254.169.254/latest/meta-data/public-ipv4 >> /var/www/html/index.html
                       echo "<hr>Here is an image that I have stored on S3: <br>" >> /var/www/html/index.html
                       echo "<img src="%s">" >> /var/www/html/index.html
                       """ % image_url)#installs apache web server thing
    print (instance[0].id)
    while not instance[0].public_ip_address:
        try:
            instance[0].reload()
            if instance[0].public_ip_address:
                # Public IP address is available
                public_ip = instance[0].public_ip_address
                print(instance[0].public_ip_address)
                return instance[0].public_ip_address
        except Exception as e:
            print("Error on create")

def create_bucket():
    s3 = boto3.resource("s3")
    bucket_name = input("Enter bucket name: ")
    try:
        response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        print (response)
        return bucket_name
    except Exception as error:
        print (error)


def put_image_bucket(bucket_name):
    s3 = boto3.client('s3')
    bucket = bucket_name
    file_name = './icon.png'
    key_name = 'icon.png'
    s3.upload_file(file_name, bucket, key_name, ExtraArgs={'ACL': 'public-read'})
    image_url = "https://s3-eu-west-1.amazonaws.com/" + bucket_name + "/" + key_name
    return image_url

def ssh_onto_server(instance_ip):
    print(instance_ip)
    ssh_command = "ssh -tt -o StrictHostKeyChecking=no -i ~/Documents/CRea_KeyPair.pem ec2-user@"\
                  +instance_ip + " python3 check_webserver"
    scp = "scp -i ~/Documents/CRea_KeyPair.pem check_webserver.py ec2-user@" +instance_ip +":."
    subprocess.run(scp, shell=True)
    #subprocess.run("python3 check_webserver")
    subprocess.run(ssh_command, check=True, shell=True)

# ssh -t -i ~/Documents/CRea_KeyPair.pem ec2-user@52.19.206.250
if __name__ == '__main__':
    main()
