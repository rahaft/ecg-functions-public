# Kaggle Notebook: Transfer Competition Data to Google Cloud Storage
# Run this in your Kaggle notebook with competition data attached
# Using Google Cloud account: hi@pathomap.co
# Project: hv-ecg

from google.cloud import storage
import os
from pathlib import Path
import json
from datetime import datetime
from tqdm import tqdm

# Configuration
COMPETITION_NAME = "physionet-ecg-image-digitization"
PROJECT_ID = "hv-ecg"  # Your Google Cloud project ID
BUCKET_PREFIX = "ecg-competition-data"
NUM_BUCKETS = 5
GCS_PREFIX = "kaggle-data/physionet-ecg/"

# Initialize GCS client (will use hi@pathomap.co account)
storage_client = storage.Client(project=PROJECT_ID)
print(f"✓ Connected to GCS project: {PROJECT_ID}")

# Get bucket list
buckets = [f"{BUCKET_PREFIX}-{i}" for i in range(1, NUM_BUCKETS + 1)]

# Verify buckets exist
print("\n📁 Verifying buckets...")
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
    print("\n⚠️  No buckets found! Create them first using:")
    print("   python scripts/create_multiple_gcs_buckets.py")
    raise Exception("No GCS buckets available")

# List files from competition
print(f"\n📋 Listing files from competition: {COMPETITION_NAME}")

# Competition data is in /kaggle/input/physionet-ecg-image-digitization/
input_dir = Path('/kaggle/input') / COMPETITION_NAME

if not input_dir.exists():
    print(f"✗ Input directory not found: {input_dir}")
    print("Make sure the competition dataset is attached to this notebook")
    print("Click 'Add data' → Search for the competition → Add")
    raise Exception("Competition data not found")

print(f"✓ Input directory found: {input_dir}")

# Walk through all files
print("\n📂 Scanning for image files...")
files_list = []
for root, dirs, files in os.walk(input_dir):
    for filename in files:
        file_path = Path(root) / filename
        relative_path = file_path.relative_to(input_dir)
        
        # Get file size
        size = file_path.stat().st_size
        
        # Determine if train/test
        is_train = 'train' in str(relative_path).lower() or str(relative_path).startswith('train')
        is_test = 'test' in str(relative_path).lower() or str(relative_path).startswith('test')
        
        # Check if image
        is_image = any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff'])
        
        # Extract folder structure
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

print(f"✓ Found {len(files_list)} total files")

# Show breakdown
image_files = [f for f in files_list if f['is_image']]
train_images = [f for f in image_files if f['is_train']]
test_images = [f for f in image_files if f['is_test']]

print(f"  📸 Image files: {len(image_files)}")
print(f"    - Train: {len(train_images)}")
print(f"    - Test: {len(test_images)}")
print(f"  📄 Other files: {len(files_list) - len(image_files)}")

if len(image_files) == 0:
    print("\n⚠️  No image files found!")
    print("First 10 files found:")
    for f in files_list[:10]:
        print(f"  - {f['name']} ({f['size']} bytes)")
    raise Exception("No image files to transfer")

# Distribute files across buckets (round-robin)
print("\n📊 Distributing files across buckets...")
bucket_distribution = {}
for i, file_info in enumerate(image_files):
    bucket = existing_buckets[i % len(existing_buckets)]
    bucket_distribution[file_info['name']] = bucket

# Print distribution
print("\nBucket distribution:")
bucket_counts = {}
total_size_per_bucket = {}
for bucket in existing_buckets:
    bucket_files = [f for f, b in bucket_distribution.items() if b == bucket]
    bucket_counts[bucket] = len(bucket_files)
    total_size = sum(f['size'] for f in image_files if bucket_distribution[f['name']] == bucket)
    total_size_per_bucket[bucket] = total_size
    size_gb = total_size / (1024**3)
    print(f"  {bucket}: {len(bucket_files)} files ({size_gb:.2f} GB)")

# Transfer files
print(f"\n☁️  Transferring {len(image_files)} images to GCS...")
print("This runs directly in Kaggle - no local download needed!")
print("\nNOTE: Large transfers may take a while. Progress will be shown below.\n")

transferred = 0
failed = []
failed_details = []

for file_info in tqdm(image_files, desc="Transferring"):
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
            'source': 'kaggle',
            'uploaded_by': 'hi@pathomap.co'
        }
        
        # Upload with content type
        content_type = None
        if filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
            content_type = 'image/tiff'
        
        blob.upload_from_string(content, content_type=content_type)
        transferred += 1
        
    except Exception as e:
        error_msg = str(e)
        failed.append(filename)
        failed_details.append((filename, error_msg))
        if len(failed) <= 5:  # Only show first few errors
            print(f"\n  ⚠️  Error with {filename}: {error_msg}")

print(f"\n✓ Transfer complete: {transferred}/{len(image_files)} images")

if failed:
    print(f"\n⚠️  Failed: {len(failed)} images")
    print("First 10 failed files:")
    for filename, error in failed_details[:10]:
        print(f"  - {filename}: {error}")

# Create manifest
print("\n📝 Creating manifest...")
manifest = {
    "competition": COMPETITION_NAME,
    "transfer_date": datetime.now().isoformat(),
    "storage_type": "gcs",
    "project_id": PROJECT_ID,
    "google_account": "hi@pathomap.co",
    "buckets_used": list(set(bucket_distribution.values())),
    "total_files": len(files_list),
    "total_images": len(image_files),
    "transferred_images": transferred,
    "failed_images": len(failed),
    "images": []
}

for file_info in image_files:
    if file_info['name'] not in failed:
        bucket = bucket_distribution[file_info['name']]
        gcs_path = f"{GCS_PREFIX}{file_info['name']}"
        
        # Format file size
        size = file_info['size']
        if size < 1024:
            size_str = f"{size} Bytes"
        elif size < 1024**2:
            size_str = f"{size/1024:.2f} KB"
        elif size < 1024**3:
            size_str = f"{size/(1024**2):.2f} MB"
        else:
            size_str = f"{size/(1024**3):.2f} GB"
        
        manifest["images"].append({
            "filename": file_info['filename'],
            "full_path": file_info['name'],
            "gcs_bucket": bucket,
            "gcs_path": gcs_path,
            "gcs_url": f"gs://{bucket}/{gcs_path}",
            "gcs_public_url": f"https://storage.googleapis.com/{bucket}/{gcs_path}",
            "size": file_info['size'],
            "size_formatted": size_str,
            "is_train": file_info['is_train'],
            "is_test": file_info['is_test'],
            "folder": file_info['folder'],
            "metadata": {
                "uploaded_at": datetime.now().isoformat(),
                "source": "kaggle",
                "competition": COMPETITION_NAME,
                "uploaded_by": "hi@pathomap.co"
            }
        })

# Save manifest to Kaggle output
manifest_path = Path('/kaggle/working') / 'image_manifest_gcs.json'
with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"✓ Manifest saved: {manifest_path}")
print(f"  You can download this file from the output panel")

# Summary
print("\n" + "=" * 70)
print("✨ Transfer Complete!")
print("=" * 70)
print(f"📊 Images transferred: {transferred}/{len(image_files)}")
print(f"📁 Buckets used: {len(set(bucket_distribution.values()))}")
print(f"📄 Manifest: image_manifest_gcs.json")
print(f"☁️  Project: {PROJECT_ID}")
print(f"👤 Account: hi@pathomap.co")
print("=" * 70)
print("\n✅ Next steps:")
print("1. Download 'image_manifest_gcs.json' from the output panel")
print("2. Save it to your local project directory")
print("3. Import to Firestore:")
print("   python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json")
