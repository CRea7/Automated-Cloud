#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError

def main():
    security_group_id = create_security()
    create_instance(security_group_id)

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
#KeyPair = CRea_KeyPair.pem
def create_instance(security_group_id):

    ec2 = boto3.resource('ec2')
    instance = ec2.create_instances(
        ImageId='ami-047bb4163c506cd98',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group_id],
        #KeyName = KeyPair,   #key pair located in dcuments
        InstanceType='t2.micro')
    print (instance[0].id)


if __name__ == '__main__':
    main()
