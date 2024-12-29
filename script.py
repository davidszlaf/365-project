#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
from collections import defaultdict
import json
from typing import Dict, List

class AWSResourceExplorer:
    def __init__(self):
        self.session = boto3.Session()
        self.regions = self.session.get_available_regions('ec2')
        
    def get_region_services(self) -> Dict[str, List[str]]:
        """List AWS services available in each region."""
        region_services = defaultdict(list)
        
        for region in self.regions:
            print(f"\nExploring region: {region}")
            session = boto3.Session(region_name=region)
            
            # Get available services in this region
            for service in boto3.Session().get_available_services():
                try:
                    session.client(service)
                    region_services[region].append(service)
                except ClientError:
                    continue
                except Exception:
                    continue
                    
        return region_services

    def get_ec2_details(self, region: str) -> Dict:
        """Get EC2 instance details in a region."""
        ec2 = boto3.client('ec2', region_name=region)
        instances = []
        
        try:
            response = ec2.describe_instances()
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'InstanceId': instance['InstanceId'],
                        'InstanceType': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'LaunchTime': instance['LaunchTime'].isoformat(),
                        'Tags': instance.get('Tags', [])
                    })
        except ClientError as e:
            print(f"Error getting EC2 details in {region}: {e}")
            
        return {'Instances': instances}

    def get_rds_details(self, region: str) -> Dict:
        """Get RDS instance details in a region."""
        rds = boto3.client('rds', region_name=region)
        instances = []
        
        try:
            response = rds.describe_db_instances()
            for instance in response['DBInstances']:
                instances.append({
                    'DBInstanceIdentifier': instance['DBInstanceIdentifier'],
                    'Engine': instance['Engine'],
                    'DBInstanceClass': instance['DBInstanceClass'],
                    'Status': instance['DBInstanceStatus']
                })
        except ClientError as e:
            print(f"Error getting RDS details in {region}: {e}")
            
        return {'DBInstances': instances}

    def get_s3_details(self) -> Dict:
        """Get S3 bucket details."""
        s3 = boto3.client('s3')
        buckets = []
        
        try:
            response = s3.list_buckets()
            for bucket in response['Buckets']:
                try:
                    region = s3.get_bucket_location(Bucket=bucket['Name'])
                    buckets.append({
                        'Name': bucket['Name'],
                        'CreationDate': bucket['CreationDate'].isoformat(),
                        'Region': region['LocationConstraint'] or 'us-east-1'
                    })
                except ClientError:
                    continue
        except ClientError as e:
            print(f"Error getting S3 details: {e}")
            
        return {'Buckets': buckets}

    def get_lambda_details(self, region: str) -> Dict:
        """Get Lambda function details in a region."""
        lambda_client = boto3.client('lambda', region_name=region)
        functions = []
        
        try:
            response = lambda_client.list_functions()
            for function in response['Functions']:
                functions.append({
                    'FunctionName': function['FunctionName'],
                    'Runtime': function['Runtime'],
                    'Memory': function['MemorySize'],
                    'Timeout': function['Timeout']
                })
        except ClientError as e:
            print(f"Error getting Lambda details in {region}: {e}")
            
        return {'Functions': functions}

def main():
    explorer = AWSResourceExplorer()
    
    # 1. List services by region
    print("\n=== AWS Services by Region ===")
    region_services = explorer.get_region_services()
    for region, services in region_services.items():
        print(f"\nRegion: {region}")
        print("Available services:", ", ".join(sorted(services)))

    # 2. Get detailed information for specific services
    print("\n=== Detailed Service Information ===")
    for region in explorer.regions:
        print(f"\nRegion: {region}")
        
        # EC2 Details
        ec2_details = explorer.get_ec2_details(region)
        if ec2_details['Instances']:
            print("\nEC2 Instances:")
            print(json.dumps(ec2_details, indent=2))
        
        # RDS Details
        rds_details = explorer.get_rds_details(region)
        if rds_details['DBInstances']:
            print("\nRDS Instances:")
            print(json.dumps(rds_details, indent=2))
        
        # Lambda Details
        lambda_details = explorer.get_lambda_details(region)
        if lambda_details['Functions']:
            print("\nLambda Functions:")
            print(json.dumps(lambda_details, indent=2))
    
    # S3 Details (Global service)
    s3_details = explorer.get_s3_details()
    if s3_details['Buckets']:
        print("\nS3 Buckets:")
        print(json.dumps(s3_details, indent=2))

if __name__ == "__main__":
    main()