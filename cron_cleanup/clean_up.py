import mysql.connector
import random
import boto3
import botocore
import os
import socket

def get_array_of_randoms(length, limit):
    randoms = []
    for x in range(length):
        candidate = random.randrange(limit)
        while candidate in randoms:
            candidate = random.randrange(limit)
        randoms.append(candidate)
    randoms = list(dict.fromkeys(randoms))
    return randoms

def trim_table(selectQuery, deleteQuery, max, toDelete, cnx):
    cursor = cnx.cursor()
    cursor.execute(selectQuery)
    IDs = cursor.fetchall()
    cursor.close()
    
    IDsDeleted = []

    if len(IDs) > max:
        randoms = get_array_of_randoms(len(IDs) - max + toDelete, len(IDs))
        print(len(randoms))
        cursor = cnx.cursor()
        # Don't delete car 1 as that is where enquiries get posted
        for x in randoms:
            if x > 8:
                cursor.execute(deleteQuery, IDs[x])
                IDsDeleted.append(IDs[x][0])
        cnx.commit()
        cursor.close()

    return IDsDeleted

def delete_s3_objects(IDsDeleted):
    s3_client = boto3.client('s3', region_name=region)
    s3_bucket_name = os.environ['BUCKET_NAME']
    for id in IDsDeleted:
        s3_client.delete_object(Bucket=s3_bucket_name, Key='IMG_' + str(id) + '.jpeg')


config = {ndidate = random.randrange(limit)
        randoms.append(candidate)
    randoms = list(dict.fromkeys(randoms))
    return randoms

def trim_table(selectQuery, deleteQuery, max, toDelete, cnx):
    cursor = cnx.cursor()
    cursor.execute(selectQuery)
    IDs = cursor.fetchall()
    cursor.close()
    
    IDsDeleted = []
  'user': os.environ["DATABASE_USERNAME"],
  'password': os.environ["DATABASE_PASSWORD"],
  'host': 'mysql-rds',
  'database': 'supercars',
  'raise_on_warnings': True
}

carsQuery = 'SELECT CAR_ID FROM CARS'
carsDelete = 'DELETE FROM CARS WHERE CAR_ID = %s'
enquiryQuery = 'SELECT ENQUIRY_ID FROM ENQUIRIES'
enquiryDelete = 'DELETE FROM ENQUIRIES WHERE ENQUIRY_ID = %s'

maxCars = 3000
carsToDelete = 2000
maxEnquiries = 3000
enquiriesToDelete = 2000

region = 'us-west-2'
securityGroup = "sg-0c793b435ce34cdd0"

print("Opening Firewall")
hostname = socket.gethostname()
myIP = socket.gethostbyname(hostname)
ec2 = boto3.client('ec2', region_name=region)
try:
    response = ec2.authorize_security_group_ingress(
        GroupId=securityGroup,
        IpPermissions=[
            {
                'FromPort': 3306,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': myIP + '/32',
                        'Description': 'MySQL access for cleanup',
                    },
                ],
                'ToPort': 3306,
            },
        ],
    )
    print(response)
except botocore.exceptions.ClientError:
    print("Failed to open firewall")

print('Start Cleanup')
cnx = mysql.connector.connect(**config)

IDsDeleted = trim_table(carsQuery, carsDelete, maxCars, carsToDelete, cnx)
print('End CARS DB cleanup')
print('Start CARS S3 cleanup')
delete_s3_objects(IDsDeleted)
print('End CARS S3 cleanup')
print('Start ENQUIRIES cleanup')
trim_table(enquiryQuery, enquiryDelete, maxEnquiries, enquiriesToDelete, cnx)
print('End ENQUIRIES cleanup')

cnx.close()

print("Closing Firewall")
try:
    response = ec2.revoke_security_group_ingress(
        GroupId=securityGroup,
        IpPermissions=[
            {
                'FromPort': 3306,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': myIP + '/32',
                        'Description': 'MySQL access for cleanup',
                    },
                ],
                'ToPort': 3306,
                
                IpPermissions=[
            {
                'FromPort': 3306,
                'IpProtocol': 'tcp',
                'IpRanges': [
                    {
                        'CidrIp': myIP + '/32',
                        'Description': 'MySQL access for cleanup',
                    },
                ],
                'ToPort': 3306,
            },
        ],
    )
    print(response)
except botocore.exceptions.ClientError:
    print("Failed to close Firewall")
