#!/usr/bin/env python3
"""
Diagnostic script to find images in GCS buckets
Helps identify where images are actually stored
"""

import sys
from google.cloud import storage

# Configuration
GCS_BUCKETS = [
    "ecg-competition-data-1",
    "ecg-competition-data-2",
    "ecg-competition-data-3",
    "ecg-competition-data-4",
    "ecg-competition-data-5"
]
PROJECT_ID = "hv-ecg"

# Image extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif']


def list_all_blobs(bucket, prefix='', max_results=100):
    """List all blobs in a bucket, optionally with a prefix"""
    try:
        blobs = bucket.list_blobs(prefix=prefix, max_results=max_results)
        return list(blobs)
    except Exception as e:
        print(f"    Error: {e}")
        return []


def check_bucket(storage_client, bucket_name):
    """Check a bucket and find images"""
    print(f"\n{'='*60}")
    print(f"Checking bucket: {bucket_name}")
    print(f"{'='*60}")
    
    try:
        bucket = storage_client.bucket(bucket_name)
        
        if not bucket.exists():
            print(f"  ✗ Bucket does not exist")
            return
        
        print(f"  ✓ Bucket exists")
        
        # Check bucket size
        try:
            blobs = list(bucket.list_blobs(max_results=1))
            if blobs:
                print(f"  ✓ Bucket has files")
            else:
                print(f"  ⚠ Bucket appears empty")
        except:
            pass
        
        # Try different prefixes
        prefixes_to_try = [
            '',  # Root
            'kaggle-data/',
            'kaggle-data/physionet-ecg/',
            'physionet-ecg/',
            'train/',
            'test/',
            'images/',
            'data/',
        ]
        
        print(f"\n  Scanning for images with different prefixes...")
        
        for prefix in prefixes_to_try:
            blobs = list_all_blobs(bucket, prefix, max_results=50)
            
            if blobs:
                # Count images
                image_count = 0
                sample_files = []
                
                for blob in blobs:
                    if any(blob.name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                        image_count += 1
                        if len(sample_files) < 3:
                            sample_files.append(blob.name)
                
                if image_count > 0:
                    print(f"\n  ✓ FOUND IMAGES!")
                    print(f"     Prefix: '{prefix}' (or empty)")
                    print(f"     Images found: {image_count}+ (showing first 50)")
                    print(f"     Sample files:")
                    for f in sample_files[:3]:
                        print(f"       - {f}")
                    return prefix
                elif len(blobs) > 0:
                    print(f"     Prefix '{prefix}': {len(blobs)} files (no images yet)")
        
        # If no prefix worked, list root level files
        print(f"\n  Checking root level...")
        root_blobs = list_all_blobs(bucket, '', max_results=20)
        if root_blobs:
            print(f"  Root level files (first 20):")
            for blob in root_blobs[:20]:
                is_image = any(blob.name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
                marker = "🖼️" if is_image else "📄"
                print(f"    {marker} {blob.name} ({blob.size:,} bytes)")
        
        return None
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("GCS Bucket Diagnostic Tool")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Buckets to check: {len(GCS_BUCKETS)}")
    print()
    
    # Initialize GCS client
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        print("✓ GCS client initialized")
    except Exception as e:
        print(f"✗ Error initializing GCS client: {e}")
        print("\nMake sure you're authenticated:")
        print("  gcloud auth application-default login")
        return
    
    # Check each bucket
    found_prefixes = {}
    
    for bucket_name in GCS_BUCKETS:
        prefix = check_bucket(storage_client, bucket_name)
        if prefix is not None:
            found_prefixes[bucket_name] = prefix
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    if found_prefixes:
        print("\n✓ Images found in buckets:")
        for bucket, prefix in found_prefixes.items():
            print(f"  - {bucket}: prefix = '{prefix}'")
        print("\n💡 Update list_gcs_images.py with the correct prefix!")
    else:
        print("\n⚠ No images found in any bucket")
        print("\nPossible reasons:")
        print("  1. Images haven't been transferred from Kaggle yet")
        print("  2. Images are in different buckets")
        print("  3. Images are in a different project")
        print("  4. Authentication/permissions issue")
        print("\nNext steps:")
        print("  1. Verify images were transferred: python scripts/kaggle_to_gcs_transfer.py")
        print("  2. Check Google Cloud Console: https://console.cloud.google.com/storage")
        print("  3. Verify project ID and bucket names are correct")


if __name__ == '__main__':
    main()
