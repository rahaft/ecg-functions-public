#!/usr/bin/env python3
"""
List all images from GCS buckets and generate a manifest JSON
This can be used by the gallery to know which images to display
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from google.cloud import storage

# Configuration
GCS_BUCKETS = [
    "ecg-competition-data-1",
    "ecg-competition-data-2",
    "ecg-competition-data-3",
    "ecg-competition-data-4",
    "ecg-competition-data-5"
]
# Try multiple prefixes - will search all of them
GCS_PREFIXES = [
    "kaggle-data/physionet-ecg/",  # Default
    "kaggle-data/",  # Alternative
    "",  # Root level
    "train/",
    "test/",
    "images/",
]
PROJECT_ID = "hv-ecg"
OUTPUT_FILE = "gcs_images_manifest.json"

# Image extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.gif']


def list_images_in_bucket(storage_client, bucket_name, prefix):
    """List all image files in a GCS bucket"""
    try:
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            print(f"  ⚠ Bucket {bucket_name} does not exist")
            return []
        
        blobs = bucket.list_blobs(prefix=prefix)
        images = []
        
        for blob in blobs:
            if any(blob.name.lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                # Generate public URL
                public_url = f"https://storage.googleapis.com/{bucket_name}/{blob.name}"
                
                images.append({
                    'name': Path(blob.name).name,  # Just filename
                    'path': blob.name,  # Full path in bucket
                    'bucket': bucket_name,
                    'url': public_url,
                    'size': blob.size,
                    'updated': blob.updated.isoformat() if blob.updated else None
                })
        
        return images
    except Exception as e:
        print(f"  ✗ Error listing {bucket_name}: {e}")
        return []


def main():
    print("=" * 60)
    print("List Images from GCS Buckets")
    print("=" * 60)
    print(f"Buckets: {', '.join(GCS_BUCKETS)}")
    print(f"Prefix: {GCS_PREFIX}")
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
    
    # Collect all images - try all prefixes
    print("\n📋 Scanning GCS buckets...")
    all_images = []
    found_prefix = None
    
    for bucket_name in GCS_BUCKETS:
        print(f"  Checking {bucket_name}...")
        
        # Try each prefix until we find images
        for prefix in GCS_PREFIXES:
            images = list_images_in_bucket(storage_client, bucket_name, prefix)
            if images:
                all_images.extend(images)
                found_prefix = prefix
                print(f"    ✓ Found {len(images)} images with prefix: '{prefix}'")
                break  # Found images, move to next bucket
        else:
            print(f"    ⚠ No images found in {bucket_name}")
    
    # If we found images, update the prefix for the manifest
    if found_prefix:
        GCS_PREFIX = found_prefix
        print(f"\n✓ Using prefix: '{GCS_PREFIX}'")
    
    if not all_images:
        print("\n⚠ No images found!")
        return
    
    print(f"\n✓ Total images: {len(all_images)}")
    
    # Create manifest
    manifest = {
        'generated_at': datetime.now().isoformat(),
        'total_images': len(all_images),
        'buckets': GCS_BUCKETS,
        'prefix': GCS_PREFIX,
        'images': all_images
    }
    
    # Save manifest
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✓ Manifest saved to: {OUTPUT_FILE}")
    print(f"   Use this file to update the gallery or serve via API")


if __name__ == '__main__':
    main()
