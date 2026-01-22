#!/usr/bin/env python3
"""
Script to make GCS buckets public for reading.
This allows images to be accessed via public URLs without signed URLs.
"""

from google.cloud import storage
import os
import sys

# List of buckets to make public
BUCKETS = [
    'ecg-competition-data-1',
    'ecg-competition-data-2',
    'ecg-competition-data-3',
    'ecg-competition-data-4',
    'ecg-competition-data-5',
]

def make_bucket_public(bucket_name, client):
    """Make a GCS bucket public for reading."""
    try:
        bucket = client.bucket(bucket_name)
        
        # Check if bucket exists
        if not bucket.exists():
            print(f"[ERROR] Bucket {bucket_name} does not exist")
            return False
        
        # Get current IAM policy
        policy = bucket.get_iam_policy(requested_policy_version=3)
        
        # Check if already public
        is_public = False
        for binding in policy.bindings:
            if binding['role'] == 'roles/storage.objectViewer' and 'allUsers' in binding.get('members', []):
                is_public = True
                break
        
        if is_public:
            print(f"[OK] {bucket_name} is already public")
            return True
        
        # Add public access
        # Find existing binding or create new one
        found = False
        for binding in policy.bindings:
            if binding['role'] == 'roles/storage.objectViewer':
                if 'allUsers' not in binding.get('members', []):
                    binding['members'].add('allUsers')
                found = True
                break
        
        if not found:
            policy.bindings.append({
                "role": "roles/storage.objectViewer",
                "members": {"allUsers"}
            })
        
        bucket.set_iam_policy(policy)
        print(f"[OK] Made {bucket_name} public")
        return True
    except Exception as e:
        print(f"[ERROR] Error making {bucket_name} public: {e}")
        return False

def main():
    # Check for service account key
    service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
    if not os.path.exists(service_account_path):
        service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'service-account-key.json')
    
    if os.path.exists(service_account_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_path
        print(f"Using service account: {service_account_path}")
    elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        print(f"Using service account from environment: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
    else:
        print("ERROR: No service account credentials found!")
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("Or place serviceAccountKey.json in the project root")
        sys.exit(1)
    
    print("Making GCS buckets public for reading...")
    print("=" * 50)
    
    try:
        client = storage.Client(project='hv-ecg')
    except Exception as e:
        print(f"ERROR: Failed to create storage client: {e}")
        print("\nMake sure:")
        print("1. Service account key file exists and is valid")
        print("2. Service account has 'Storage Admin' or 'Storage Object Admin' role")
        sys.exit(1)
    
    success_count = 0
    for bucket_name in BUCKETS:
        if make_bucket_public(bucket_name, client):
            success_count += 1
    
    print("=" * 50)
    print(f"Completed: {success_count}/{len(BUCKETS)} buckets made public")
    
    if success_count == len(BUCKETS):
        print("\n[SUCCESS] All buckets are now public!")
        print("Images should now load in the gallery.")
    else:
        print("\n[WARNING] Some buckets failed. Check the errors above.")

if __name__ == '__main__':
    main()
