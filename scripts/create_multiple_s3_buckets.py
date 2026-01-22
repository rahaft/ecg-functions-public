#!/usr/bin/env python3
"""
Create multiple S3 buckets for organizing competition data
Distributes data across buckets to stay within free tier limits
"""

import boto3
import sys
from botocore.exceptions import ClientError

# Configuration
NUM_BUCKETS = 5
BUCKET_PREFIX = "ecg-competition-data"
REGION = "us-east-1"  # Cheapest region


def create_buckets(num_buckets, prefix, region):
    """Create multiple S3 buckets"""
    s3_client = boto3.client('s3', region_name=region)
    
    created_buckets = []
    failed_buckets = []
    
    print(f"Creating {num_buckets} S3 buckets...")
    print(f"Region: {region}")
    print(f"Prefix: {prefix}")
    print("=" * 60)
    
    for i in range(1, num_buckets + 1):
        bucket_name = f"{prefix}-{i}"
        
        try:
            # Check if bucket already exists
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                print(f"✓ Bucket {bucket_name} already exists")
                created_buckets.append(bucket_name)
                continue
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code != '404':
                    raise
            
            # Create bucket
            if region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            # Configure bucket settings
            # Block public access
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            # Enable encryption
            s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
            
            # Set lifecycle policy to move to Glacier after 30 days
            s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    'Rules': [{
                        'Id': 'MoveToGlacier',
                        'Status': 'Enabled',
                        'Transitions': [{
                            'Days': 30,
                            'StorageClass': 'GLACIER'
                        }]
                    }, {
                        'Id': 'DeleteIncompleteUploads',
                        'Status': 'Enabled',
                        'AbortIncompleteMultipartUpload': {
                            'DaysAfterInitiation': 7
                        }
                    }]
                }
            )
            
            print(f"✓ Created bucket: {bucket_name}")
            created_buckets.append(bucket_name)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"⚠ Bucket {bucket_name} already exists (owned by another account)")
            elif error_code == 'BucketAlreadyOwnedByYou':
                print(f"✓ Bucket {bucket_name} already exists")
                created_buckets.append(bucket_name)
            else:
                print(f"✗ Failed to create {bucket_name}: {e}")
                failed_buckets.append(bucket_name)
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Created: {len(created_buckets)} buckets")
    if failed_buckets:
        print(f"  Failed: {len(failed_buckets)} buckets")
        for bucket in failed_buckets:
            print(f"    - {bucket}")
    
    return created_buckets


def list_buckets():
    """List all buckets"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        
        print(f"\nYour S3 Buckets ({len(buckets)} total):")
        for bucket in buckets:
            print(f"  - {bucket}")
        
        return buckets
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return []


def main():
    print("=" * 60)
    print("AWS S3 Multiple Buckets Setup")
    print("=" * 60)
    
    # Check AWS credentials
    try:
        s3_client = boto3.client('s3')
        # Test connection
        s3_client.list_buckets()
        print("✓ AWS credentials configured")
    except Exception as e:
        print(f"✗ AWS credentials not configured: {e}")
        print("\nPlease run: aws configure")
        print("Or set environment variables:")
        print("  AWS_ACCESS_KEY_ID")
        print("  AWS_SECRET_ACCESS_KEY")
        print("  AWS_DEFAULT_REGION")
        sys.exit(1)
    
    # Create buckets
    created = create_buckets(NUM_BUCKETS, BUCKET_PREFIX, REGION)
    
    # List all buckets
    list_buckets()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Verify buckets in AWS Console")
    print("2. Set up billing alerts")
    print("3. Update transfer script with bucket names")
    print("=" * 60)
    
    # Save bucket list
    with open('s3_buckets.txt', 'w') as f:
        for bucket in created:
            f.write(f"{bucket}\n")
    
    print(f"\n✓ Bucket list saved to: s3_buckets.txt")


if __name__ == "__main__":
    main()
