#!/usr/bin/env python3
"""
Kaggle to GCS Transfer V2
Uses Bearer token authentication (works with KGAT_ tokens)
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import tempfile

# Configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
BUCKET_PREFIX = "ecg-competition-data"
NUM_BUCKETS = 5
GCS_PREFIX = "kaggle-data/physionet-ecg/"

try:
    from google.cloud import storage
except ImportError:
    print("Error: google-cloud-storage not installed")
    print("Install with: pip install google-cloud-storage")
    sys.exit(1)


def load_kaggle_credentials():
    """Load Kaggle credentials from kaggle.json"""
    kaggle_file = Path.home() / '.kaggle' / 'kaggle.json'
    
    if not kaggle_file.exists():
        print(f"Error: {kaggle_file} not found")
        sys.exit(1)
    
    with open(kaggle_file, 'r') as f:
        config = json.load(f)
        return config.get('username'), config.get('key')


def list_competition_files(token):
    """List files in competition using Bearer token auth"""
    url = f"https://www.kaggle.com/api/v1/competitions/data/list/{COMPETITION_NAME}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error listing files: {response.status_code}")
        print(f"Response: {response.text}")
        return []
    
    files = response.json()
    
    file_list = []
    for f in files:
        name = f.get('name', '')
        size = f.get('totalBytes', 0)
        
        is_train = 'train' in name.lower()
        is_test = 'test' in name.lower()
        
        folder_parts = name.split('/')
        folder_path = '/'.join(folder_parts[:-1]) if len(folder_parts) > 1 else ''
        filename = folder_parts[-1] if folder_parts else name
        
        is_image = any(name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff'])
        
        file_list.append({
            'name': name,
            'filename': filename,
            'size': size,
            'size_formatted': format_file_size(size),
            'is_train': is_train,
            'is_test': is_test,
            'folder': folder_path,
            'is_image': is_image,
            'url': f.get('url', '')
        })
    
    return file_list


def download_file(token, filename):
    """Download a single file from competition"""
    url = f"https://www.kaggle.com/api/v1/competitions/data/download/{COMPETITION_NAME}/{filename}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code != 200:
        print(f"Error downloading {filename}: {response.status_code}")
        return None
    
    return response.content


def format_file_size(bytes):
    """Format file size"""
    if bytes == 0:
        return '0 Bytes'
    k = 1024
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    import math
    i = int(math.floor(math.log(bytes) / math.log(k)))
    return f"{round(bytes / (k ** i), 2)} {sizes[i]}"


def get_bucket_list():
    """Get list of available buckets"""
    buckets = []
    for i in range(1, NUM_BUCKETS + 1):
        buckets.append(f"{BUCKET_PREFIX}-{i}")
    return buckets


def select_bucket_for_file(index, buckets):
    """Distribute files across buckets using round-robin"""
    return buckets[index % len(buckets)]


def upload_to_gcs(storage_client, bucket_name, blob_name, content, metadata=None):
    """Upload content to GCS"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        if metadata:
            blob.metadata = metadata
        
        blob.upload_from_string(content)
        return True
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        return False


def create_manifest(files_list, bucket_distribution):
    """Create manifest with bucket assignments"""
    manifest = {
        "competition": COMPETITION_NAME,
        "transfer_date": datetime.now().isoformat(),
        "storage_type": "gcs",
        "buckets_used": list(set(bucket_distribution.values())),
        "total_files": len(files_list),
        "images": []
    }
    
    for file_info in files_list:
        if file_info.get('transferred'):
            bucket = bucket_distribution.get(file_info['name'], 'unknown')
            gcs_path = f"{GCS_PREFIX}{file_info['name']}"
            
            manifest["images"].append({
                "filename": file_info['filename'],
                "full_path": file_info['name'],
                "gcs_bucket": bucket,
                "gcs_path": gcs_path,
                "gcs_url": f"gs://{bucket}/{gcs_path}",
                "gcs_public_url": f"https://storage.googleapis.com/{bucket}/{gcs_path}",
                "size": file_info['size'],
                "size_formatted": file_info['size_formatted'],
                "is_train": file_info['is_train'],
                "is_test": file_info['is_test'],
                "folder": file_info['folder'],
                "metadata": {
                    "uploaded_at": datetime.now().isoformat(),
                    "source": "kaggle",
                    "competition": COMPETITION_NAME
                }
            })
    
    return manifest


def main():
    print("=" * 70)
    print("Kaggle to GCS Transfer V2 (Bearer Token Auth)")
    print("=" * 70)
    print(f"Competition: {COMPETITION_NAME}")
    print(f"Buckets: {BUCKET_PREFIX}-1 through {BUCKET_PREFIX}-{NUM_BUCKETS}")
    print("=" * 70)
    
    # Load credentials
    username, token = load_kaggle_credentials()
    print(f"Username: {username}")
    print(f"Token: {token[:20]}...")
    
    # Initialize GCS client
    try:
        storage_client = storage.Client(project='hv-ecg')
        print(f"GCS connected to project: {storage_client.project}")
    except Exception as e:
        print(f"GCS connection failed: {e}")
        sys.exit(1)
    
    # Get bucket list
    buckets = get_bucket_list()
    existing_buckets = []
    
    print("\nVerifying buckets...")
    for bucket_name in buckets:
        try:
            bucket = storage_client.bucket(bucket_name)
            if bucket.exists():
                existing_buckets.append(bucket_name)
                print(f"  OK: {bucket_name}")
        except Exception as e:
            print(f"  Error: {bucket_name}: {e}")
    
    if not existing_buckets:
        print("No buckets found!")
        sys.exit(1)
    
    # List files from Kaggle
    print("\nGetting file list from Kaggle...")
    files_list = list_competition_files(token)
    
    if not files_list:
        print("No files found!")
        sys.exit(1)
    
    print(f"Found {len(files_list)} files")
    
    # Show what we found
    print("\nFiles found:")
    for f in files_list:
        print(f"  - {f['name']} ({f['size_formatted']}) {'[IMAGE]' if f['is_image'] else ''}")
    
    # Filter for files to transfer (all files, not just images since competition might have zip/csv)
    files_to_transfer = files_list  # Transfer all files
    
    print(f"\nTotal files to transfer: {len(files_to_transfer)}")
    
    # Distribute files across buckets
    bucket_distribution = {}
    for i, file_info in enumerate(files_to_transfer):
        bucket = select_bucket_for_file(i, existing_buckets)
        bucket_distribution[file_info['name']] = bucket
    
    # Print distribution
    print("\nBucket distribution:")
    bucket_counts = {}
    for bucket in existing_buckets:
        count = sum(1 for f, b in bucket_distribution.items() if b == bucket)
        bucket_counts[bucket] = count
        print(f"  {bucket}: {count} files")
    
    # Transfer files
    print(f"\nTransferring {len(files_to_transfer)} files...")
    print("\nNOTE: This downloads one file at a time and uploads to GCS")
    print("      Files are NOT stored on your computer\n")
    
    transferred = 0
    failed = []
    
    for file_info in tqdm(files_to_transfer, desc="Transferring"):
        filename = file_info['name']
        bucket = bucket_distribution[filename]
        gcs_blob_name = f"{GCS_PREFIX}{filename}"
        
        # Download from Kaggle
        content = download_file(token, filename)
        
        if content is None:
            failed.append(filename)
            continue
        
        # Upload to GCS
        metadata = {
            'is_train': str(file_info['is_train']),
            'is_test': str(file_info['is_test']),
            'folder': file_info['folder'],
            'competition': COMPETITION_NAME,
            'source': 'kaggle'
        }
        
        if upload_to_gcs(storage_client, bucket, gcs_blob_name, content, metadata):
            transferred += 1
            file_info['transferred'] = True
        else:
            failed.append(filename)
    
    print(f"\nTransfer complete: {transferred}/{len(files_to_transfer)} files")
    
    if failed:
        print(f"Failed: {len(failed)} files")
        for f in failed[:10]:
            print(f"  - {f}")
    
    # Create manifest
    print("\nCreating manifest...")
    manifest = create_manifest(files_list, bucket_distribution)
    
    manifest_file = Path("image_manifest_gcs.json")
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest saved: {manifest_file}")
    
    print("\n" + "=" * 70)
    print("Transfer Complete!")
    print(f"Files: {transferred}")
    print(f"Buckets used: {len(set(bucket_distribution.values()))}")
    print(f"Manifest: {manifest_file}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTransfer interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
