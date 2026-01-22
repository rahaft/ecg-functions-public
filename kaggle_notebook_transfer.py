# Kaggle Notebook: Transfer Competition Data to Google Cloud Storage
# Run this in a Kaggle notebook with Google Cloud Services enabled

# Install required packages (if needed)
# !pip install google-cloud-storage

from google.cloud import storage
import os
from pathlib import Path
import json
from datetime import datetime

# Configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
PROJECT_ID = "hv-ecg"  # Your Google Cloud project ID
BUCKET_PREFIX = "ecg-competition-data"
NUM_BUCKETS = 5
GCS_PREFIX = "kaggle-data/physionet-ecg/"

# Initialize GCS client
storage_client = storage.Client(project=PROJECT_ID)
print(f"✓ Connected to GCS project: {PROJECT_ID}")

# Get bucket list
buckets = [f"{BUCKET_PREFIX}-{i}" for i in range(1, NUM_BUCKETS + 1)]

# Verify buckets exist
print("\nVerifying buckets...")
existing_buckets = []
for bucket_name in buckets:
    try:
        bucket = storage_client.bucket(bucket_name)
        if bucket.exists():
            existing_buckets.append(bucket_name)
            print(f"  ✓ {bucket_name}")
        else:
            print(f"  ✗ {bucket_name} (not found)")
    except Exception as e:
        print(f"  ✗ {bucket_name} (error: {e})")

if not existing_buckets:
    print("\nNo buckets found! Create them first.")
    raise Exception("No GCS buckets available")

# List files from competition
print(f"\n📋 Listing files from competition: {COMPETITION_NAME}")

# Files are in /kaggle/input/physionet-ecg-image-digitization/
input_dir = Path('/kaggle/input') / COMPETITION_NAME

if not input_dir.exists():
    print(f"✗ Input directory not found: {input_dir}")
    print("Make sure the competition dataset is attached to this notebook")
    raise Exception("Competition data not found")

# Walk through all files
files_list = []
for root, dirs, files in os.walk(input_dir):
    for filename in files:
        file_path = Path(root) / filename
        relative_path = file_path.relative_to(input_dir)
        
        # Get file size
        size = file_path.stat().st_size
        
        # Determine if train/test
        is_train = 'train' in str(relative_path).lower()
        is_test = 'test' in str(relative_path).lower()
        
        # Check if image
        is_image = any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff'])
        
        folder_parts = str(relative_path).split('/')
        folder_path = '/'.join(folder_parts[:-1]) if len(folder_parts) > 1 else ''
        
        files_list.append({
            'name': str(relative_path),
            'filename': filename,
            'full_path': str(file_path),
            'size': size,
            'is_train': is_train,
            'is_test': is_test,
            'folder': folder_path,
            'is_image': is_image
        })

print(f"✓ Found {len(files_list)} files")

# Filter for images (or all files if you want everything)
image_files = [f for f in files_list if f['is_image']]
print(f"  - {len(image_files)} image files")
print(f"  - Train: {sum(1 for f in image_files if f['is_train'])}")
print(f"  - Test: {sum(1 for f in image_files if f['is_test'])}")

# Distribute files across buckets
print("\n📊 Distributing files across buckets...")
bucket_distribution = {}
for i, file_info in enumerate(image_files):
    bucket = existing_buckets[i % len(existing_buckets)]
    bucket_distribution[file_info['name']] = bucket

# Print distribution
print("\nBucket distribution:")
for bucket in existing_buckets:
    count = sum(1 for f, b in bucket_distribution.items() if b == bucket)
    print(f"  {bucket}: {count} files")

# Transfer files
print(f"\n☁️  Transferring {len(image_files)} images to GCS...")
print("This runs directly in Kaggle - no local download needed!")

transferred = 0
failed = []

for file_info in image_files:
    filename = file_info['name']
    file_path = file_info['full_path']
    bucket = bucket_distribution[filename]
    gcs_blob_name = f"{GCS_PREFIX}{filename}"
    
    try:
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Upload to GCS
        bucket_obj = storage_client.bucket(bucket)
        blob = bucket_obj.blob(gcs_blob_name)
        
        # Set metadata
        blob.metadata = {
            'is_train': str(file_info['is_train']),
            'is_test': str(file_info['is_test']),
            'folder': file_info['folder'],
            'competition': COMPETITION_NAME,
            'source': 'kaggle'
        }
        
        blob.upload_from_string(content)
        transferred += 1
        
        if transferred % 10 == 0:
            print(f"  Transferred {transferred}/{len(image_files)}...")
            
    except Exception as e:
        print(f"  ✗ Error transferring {filename}: {e}")
        failed.append(filename)

print(f"\n✓ Transfer complete: {transferred}/{len(image_files)} images")

if failed:
    print(f"⚠️  Failed: {len(failed)} images")
    for f in failed[:10]:
        print(f"  - {f}")

# Create manifest
print("\n📝 Creating manifest...")
manifest = {
    "competition": COMPETITION_NAME,
    "transfer_date": datetime.now().isoformat(),
    "storage_type": "gcs",
    "buckets_used": list(set(bucket_distribution.values())),
    "total_files": len(files_list),
    "images": []
}

for file_info in image_files:
    if file_info['name'] not in failed:
        bucket = bucket_distribution[file_info['name']]
        gcs_path = f"{GCS_PREFIX}{file_info['name']}"
        
        manifest["images"].append({
            "filename": file_info['filename'],
            "full_path": file_info['name'],
            "gcs_bucket": bucket,
            "gcs_path": gcs_path,
            "gcs_url": f"gs://{bucket}/{gcs_path}",
            "gcs_public_url": f"https://storage.googleapis.com/{bucket}/{gcs_path}",
            "size": file_info['size'],
            "is_train": file_info['is_train'],
            "is_test": file_info['is_test'],
            "folder": file_info['folder'],
            "metadata": {
                "uploaded_at": datetime.now().isoformat(),
                "source": "kaggle",
                "competition": COMPETITION_NAME
            }
        })

# Save manifest to Kaggle output
manifest_path = Path('/kaggle/working') / 'image_manifest_gcs.json'
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"✓ Manifest saved: {manifest_path}")

print("\n" + "=" * 70)
print("✨ Transfer Complete!")
print(f"📊 Images: {transferred}")
print(f"📁 Buckets used: {len(set(bucket_distribution.values()))}")
print("=" * 70)
