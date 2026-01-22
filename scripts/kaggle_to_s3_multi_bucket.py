#!/usr/bin/env python3
"""
Kaggle to S3 Transfer - Multiple Buckets
Distributes files across multiple buckets to optimize storage
"""

import os
import sys
import boto3
import json
from pathlib import Path
from tqdm import tqdm
import time
from datetime import datetime
import hashlib

# Configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
BUCKET_PREFIX = "ecg-competition-data"  # Will use buckets 1-5
NUM_BUCKETS = 5
S3_PREFIX = "kaggle-data/physionet-ecg/"
TEMP_DIR = os.environ.get('TEMP_DIR', '/tmp/kaggle_transfer')
MAX_BUCKET_SIZE = 20 * 1024 * 1024 * 1024  # 20GB per bucket (approximate limit)


def get_bucket_list():
    """Get list of available buckets"""
    buckets = []
    for i in range(1, NUM_BUCKETS + 1):
        buckets.append(f"{BUCKET_PREFIX}-{i}")
    return buckets


def select_bucket_for_file(file_size, bucket_usage, buckets):
    """
    Select bucket for file based on current usage
    Distributes files evenly across buckets
    """
    # Find bucket with least usage
    min_usage = min(bucket_usage.values())
    min_buckets = [b for b, usage in bucket_usage.items() if usage == min_usage]
    
    # If all buckets are under limit, use round-robin
    if min_usage < MAX_BUCKET_SIZE:
        # Use hash of filename for consistent distribution
        bucket_index = hash(file_size) % len(min_buckets)
        return min_buckets[bucket_index]
    
    # If all buckets are full, use the one with most space
    max_available = max(bucket_usage.values())
    for bucket, usage in bucket_usage.items():
        if usage == max_available:
            return bucket
    
    # Fallback to first bucket
    return buckets[0]


def get_kaggle_files_list(competition_name):
    """Get list of files from Kaggle competition"""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        files = api.competition_list_files(competition_name)
        
        file_list = []
        for f in files:
            is_train = 'train' in f.name.lower() or 'training' in f.name.lower()
            is_test = 'test' in f.name.lower()
            
            folder_parts = f.name.split('/')
            folder_path = '/'.join(folder_parts[:-1]) if len(folder_parts) > 1 else ''
            filename = folder_parts[-1]
            
            file_list.append({
                'name': f.name,
                'filename': filename,
                'size': f.size,
                'size_formatted': format_file_size(f.size),
                'is_train': is_train,
                'is_test': is_test,
                'folder': folder_path,
                'is_image': any(f.name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']),
                'creation_date': str(f.creationDate) if hasattr(f, 'creationDate') else None
            })
        
        return file_list
    except Exception as e:
        print(f"Error listing Kaggle files: {e}")
        return []


def format_file_size(bytes):
    """Format file size"""
    if bytes == 0:
        return '0 Bytes'
    k = 1024
    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    i = int(__import__('math').floor(__import__('math').log(bytes) / __import__('math').log(k)))
    return f"{round(bytes / (k ** i), 2)} {sizes[i]}"


def stream_kaggle_to_s3(kaggle_file, s3_bucket, s3_key, s3_client):
    """Stream file from Kaggle to S3 (minimal temp storage)"""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        temp_file = Path(TEMP_DIR) / f"temp_{kaggle_file['filename']}"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download to temp
            api.competition_download_file(
                COMPETITION_NAME,
                kaggle_file['name'],
                path=str(temp_file.parent),
                quiet=True
            )
            
            # Upload to S3
            s3_client.upload_file(
                str(temp_file),
                s3_bucket,
                s3_key,
                ExtraArgs={'StorageClass': 'STANDARD'}
            )
            
        finally:
            # Always delete temp file
            if temp_file.exists():
                temp_file.unlink()
        
        return True
    except Exception as e:
        print(f"Error streaming {kaggle_file['name']}: {e}")
        return False


def create_manifest(files_list, bucket_distribution):
    """Create manifest with bucket assignments"""
    manifest = {
        "competition": COMPETITION_NAME,
        "transfer_date": datetime.now().isoformat(),
        "buckets_used": list(set(bucket_distribution.values())),
        "images": []
    }
    
    for file_info, bucket in zip(files_list, [bucket_distribution.get(f['name'], 'unknown') for f in files_list]):
        if file_info['is_image']:
            manifest["images"].append({
                "filename": file_info['filename'],
                "full_path": file_info['name'],
                "s3_bucket": bucket,
                "s3_key": f"{S3_PREFIX}{file_info['name']}",
                "s3_url": f"s3://{bucket}/{S3_PREFIX}{file_info['name']}",
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
    print("Kaggle to S3 Transfer - Multiple Buckets")
    print("=" * 70)
    print(f"Competition: {COMPETITION_NAME}")
    print(f"Buckets: {BUCKET_PREFIX}-1 through {BUCKET_PREFIX}-{NUM_BUCKETS}")
    print(f"Max per bucket: ~20GB")
    print("=" * 70)
    
    # Initialize S3
    s3_client = boto3.client('s3')
    buckets = get_bucket_list()
    
    # Verify buckets exist
    print("\nVerifying buckets...")
    existing_buckets = []
    for bucket in buckets:
        try:
            s3_client.head_bucket(Bucket=bucket)
            existing_buckets.append(bucket)
            print(f"  ✓ {bucket}")
        except:
            print(f"  ✗ {bucket} (not found - create it first)")
    
    if not existing_buckets:
        print("\nNo buckets found! Create them first:")
        print("  python scripts/create_multiple_s3_buckets.py")
        sys.exit(1)
    
    # Get file list
    print("\n📋 Getting file list from Kaggle...")
    files_list = get_kaggle_files_list(COMPETITION_NAME)
    image_files = [f for f in files_list if f['is_image']]
    
    print(f"✓ Found {len(image_files)} image files")
    
    # Distribute files across buckets
    print("\n📊 Distributing files across buckets...")
    bucket_usage = {bucket: 0 for bucket in existing_buckets}
    bucket_distribution = {}
    
    for file_info in image_files:
        bucket = select_bucket_for_file(file_info['size'], bucket_usage, existing_buckets)
        bucket_distribution[file_info['name']] = bucket
        bucket_usage[bucket] += file_info['size']
    
    # Print distribution
    print("\nBucket distribution:")
    for bucket, usage in sorted(bucket_usage.items()):
        usage_gb = usage / (1024**3)
        print(f"  {bucket}: {usage_gb:.2f} GB ({len([f for f, b in bucket_distribution.items() if b == bucket])} files)")
    
    # Transfer files
    print(f"\n☁️  Transferring {len(image_files)} images...")
    transferred = 0
    failed = []
    
    for file_info in tqdm(image_files, desc="Transferring"):
        bucket = bucket_distribution[file_info['name']]
        s3_key = f"{S3_PREFIX}{file_info['name']}"
        
        if stream_kaggle_to_s3(file_info, bucket, s3_key, s3_client):
            transferred += 1
        else:
            failed.append(file_info['name'])
    
    print(f"\n✓ Transfer complete: {transferred}/{len(image_files)} images")
    
    # Create manifest
    print("\n📝 Creating manifest...")
    manifest = create_manifest(files_list, bucket_distribution)
    
    manifest_file = Path("image_manifest_multi_bucket.json")
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Manifest saved: {manifest_file}")
    
    print("\n" + "=" * 70)
    print("✨ Transfer Complete!")
    print(f"📊 Images: {transferred}")
    print(f"📁 Buckets used: {len(set(bucket_distribution.values()))}")
    print("=" * 70)


if __name__ == "__main__":
    main()
