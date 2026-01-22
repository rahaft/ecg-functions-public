# Add this cell to your Kaggle notebook to verify and download the manifest

from pathlib import Path
import json

# Check if manifest exists
manifest_path = Path('/kaggle/working/image_manifest_gcs.json')

if manifest_path.exists():
    print("✓ Manifest file found!")
    print(f"  Location: {manifest_path}")
    print(f"  Size: {manifest_path.stat().st_size / 1024:.2f} KB")
    
    # Load and show summary
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print(f"\n📊 Manifest Summary:")
    print(f"  Competition: {manifest.get('competition', 'N/A')}")
    print(f"  Total images: {manifest.get('total_images', len(manifest.get('images', [])))}")
    print(f"  Transferred: {manifest.get('transferred_images', len(manifest.get('images', [])))}")
    print(f"  Buckets used: {len(manifest.get('buckets_used', []))}")
    
    # List buckets
    buckets = manifest.get('buckets_used', [])
    if buckets:
        print(f"\n📁 Buckets:")
        for bucket in buckets:
            count = sum(1 for img in manifest.get('images', []) if img.get('gcs_bucket') == bucket)
            print(f"  - {bucket}: {count} images")
    
    # Show first few images
    images = manifest.get('images', [])
    if images:
        print(f"\n📸 First 5 images:")
        for img in images[:5]:
            print(f"  - {img.get('filename')} ({img.get('gcs_bucket')})")
    
    print(f"\n✅ File is ready to download from the Output panel!")
    print(f"   Look for: /kaggle/working/image_manifest_gcs.json")
    
else:
    print("✗ Manifest file not found!")
    print("  Checking /kaggle/working directory...")
    
    working_dir = Path('/kaggle/working')
    if working_dir.exists():
        files = list(working_dir.glob('*.json'))
        if files:
            print(f"  Found JSON files: {[f.name for f in files]}")
        else:
            print("  No JSON files found. The manifest may not have been created.")
    else:
        print("  /kaggle/working directory doesn't exist!")
