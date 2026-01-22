#!/usr/bin/env python3
"""
Script to configure CORS on GCS buckets to allow web app access.
This allows the web app to fetch images from GCS buckets.
"""

from google.cloud import storage
import os
import sys
import json

# Configure stdout for UTF-8 to avoid encoding errors
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# List of buckets to configure
BUCKETS = [
    'ecg-competition-data-1',
    'ecg-competition-data-2',
    'ecg-competition-data-3',
    'ecg-competition-data-4',
    'ecg-competition-data-5',
]

# CORS configuration for web app access
CORS_CONFIG = [
    {
        "origin": ["https://hv-ecg.web.app", "https://hv-ecg.firebaseapp.com", "http://localhost:5000"],
        "method": ["GET", "HEAD", "OPTIONS"],
        "responseHeader": ["Content-Type", "Content-Length", "Access-Control-Allow-Origin"],
        "maxAgeSeconds": 3600
    }
]

def configure_cors(bucket_name, client):
    """Configure CORS on a GCS bucket."""
    try:
        bucket = client.bucket(bucket_name)
        
        # Check if bucket exists
        if not bucket.exists():
            print(f"[ERROR] Bucket {bucket_name} does not exist")
            return False
        
        # Set CORS configuration
        bucket.cors = CORS_CONFIG
        bucket.patch()
        
        print(f"[OK] Configured CORS for {bucket_name}")
        return True
    except Exception as e:
        print(f"[ERROR] Error configuring CORS for {bucket_name}: {e}")
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
    
    print("Configuring CORS on GCS buckets...")
    print("=" * 50)
    print(f"CORS Origins: {', '.join(CORS_CONFIG[0]['origin'])}")
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
        if configure_cors(bucket_name, client):
            success_count += 1
    
    print("=" * 50)
    print(f"Completed: {success_count}/{len(BUCKETS)} buckets configured")
    
    if success_count == len(BUCKETS):
        print("\n[SUCCESS] CORS configured on all buckets!")
        print("The web app should now be able to load images from GCS.")
    else:
        print("\n[WARNING] Some buckets failed. Check the errors above.")

if __name__ == '__main__':
    main()
