#!/usr/bin/env python3
"""
Create multiple GCS buckets for organizing competition data
Distributes data across buckets to stay within free tier limits
"""

import os
import sys
from pathlib import Path

try:
    from google.cloud import storage
    from google.api_core import exceptions
except ImportError:
    print("Error: google-cloud-storage not installed")
    print("Install with: pip install google-cloud-storage")
    sys.exit(1)

# Configuration
NUM_BUCKETS = 5
BUCKET_PREFIX = "ecg-competition-data"
PROJECT_ID = "hv-ecg"  # Your Google Cloud project ID (from service account JSON)
REGION = "us-central1"  # Cheapest region
STORAGE_CLASS = "STANDARD"


def create_buckets(num_buckets, prefix, project_id, region, storage_class):
    """Create multiple GCS buckets"""
    try:
        storage_client = storage.Client(project=project_id)
    except Exception as e:
        print(f"Error initializing GCS client: {e}")
        print("\nMake sure you have:")
        print("1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   OR run: gcloud auth application-default login")
        print("2. Installed: pip install google-cloud-storage")
        sys.exit(1)
    
    created_buckets = []
    failed_buckets = []
    
    print(f"Creating {num_buckets} GCS buckets...")
    print(f"Project: {project_id}")
    print(f"Region: {region}")
    print(f"Prefix: {prefix}")
    print("=" * 60)
    
    for i in range(1, num_buckets + 1):
        bucket_name = f"{prefix}-{i}"
        
        try:
            # Check if bucket already exists
            try:
                bucket = storage_client.bucket(bucket_name)
                if bucket.exists():
                    print(f"✓ Bucket {bucket_name} already exists")
                    created_buckets.append(bucket_name)
                    continue
            except exceptions.NotFound:
                pass
            
            # Create bucket
            bucket = storage_client.bucket(bucket_name)
            bucket.location = region
            bucket.storage_class = storage_class
            
            # Create with uniform bucket-level access
            bucket.create(
                project=project_id,
                location=region
            )
            
            # Set uniform bucket-level access (recommended)
            bucket.iam_configuration.uniform_bucket_level_access_enabled = True
            bucket.patch()
            
            # Set lifecycle rules (move to Archive after 30 days)
            lifecycle_rules = [
                {
                    'action': {'type': 'SetStorageClass', 'storageClass': 'ARCHIVE'},
                    'condition': {'age': 30}
                },
                {
                    'action': {'type': 'Delete'},
                    'condition': {'age': 365, 'matchesStorageClass': ['ARCHIVE']}
                }
            ]
            bucket.lifecycle_rules = lifecycle_rules
            bucket.patch()
            
            print(f"✓ Created bucket: {bucket_name}")
            created_buckets.append(bucket_name)
            
        except exceptions.Conflict:
            print(f"⚠ Bucket {bucket_name} already exists (owned by another project)")
        except Exception as e:
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


def list_buckets(project_id):
    """List all buckets in project"""
    try:
        storage_client = storage.Client(project=project_id)
        buckets = storage_client.list_buckets()
        
        bucket_list = [b.name for b in buckets]
        
        print(f"\nYour GCS Buckets ({len(bucket_list)} total):")
        for bucket_name in bucket_list:
            print(f"  - {bucket_name}")
        
        return bucket_list
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return []


def main():
    print("=" * 60)
    print("Google Cloud Storage Multiple Buckets Setup")
    print("=" * 60)
    
    # Check credentials
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path:
        print(f"✓ Using credentials: {creds_path}")
    else:
        print("⚠ No GOOGLE_APPLICATION_CREDENTIALS set")
        print("  Using application default credentials")
        print("  (Run: gcloud auth application-default login)")
    
    # Create buckets
    created = create_buckets(NUM_BUCKETS, BUCKET_PREFIX, PROJECT_ID, REGION, STORAGE_CLASS)
    
    # List all buckets
    list_buckets(PROJECT_ID)
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. Verify buckets in Google Cloud Console")
    print("2. Set up billing alerts")
    print("3. Update transfer script with bucket names")
    print("=" * 60)
    
    # Save bucket list
    with open('gcs_buckets.txt', 'w') as f:
        for bucket in created:
            f.write(f"{bucket}\n")
    
    print(f"\n✓ Bucket list saved to: gcs_buckets.txt")


if __name__ == "__main__":
    main()
