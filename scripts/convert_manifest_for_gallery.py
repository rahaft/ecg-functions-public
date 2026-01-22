#!/usr/bin/env python3
"""
Convert existing image_manifest_gcs.json to gallery format
"""

import json
import sys
from pathlib import Path

INPUT_FILE = "image_manifest_gcs.json"
OUTPUT_FILE = "gcs_images_manifest.json"


def convert_manifest():
    """Convert manifest to gallery format"""
    try:
        # Read existing manifest
        with open(INPUT_FILE, 'r') as f:
            old_manifest = json.load(f)
        
        print(f"✓ Loaded manifest: {len(old_manifest.get('images', []))} images")
        
        # Convert to gallery format
        gallery_manifest = {
            'generated_at': old_manifest.get('transfer_date', ''),
            'total_images': old_manifest.get('total_images', len(old_manifest.get('images', []))),
            'buckets': old_manifest.get('buckets_used', []),
            'prefix': 'kaggle-data/physionet-ecg/',
            'images': []
        }
        
        # Convert each image
        for img in old_manifest.get('images', []):
            gallery_manifest['images'].append({
                'name': img.get('filename', ''),
                'path': img.get('gcs_path', ''),
                'bucket': img.get('gcs_bucket', ''),
                'url': img.get('gcs_public_url', ''),
                'size': img.get('size', 0),
                'updated': img.get('metadata', {}).get('uploaded_at', ''),
                'is_train': img.get('is_train', False),
                'is_test': img.get('is_test', False),
                'folder': img.get('folder', '')
            })
        
        # Save gallery manifest
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(gallery_manifest, f, indent=2)
        
        print(f"✓ Converted {len(gallery_manifest['images'])} images")
        print(f"✓ Saved to: {OUTPUT_FILE}")
        print(f"\n📊 Summary:")
        print(f"   Total images: {gallery_manifest['total_images']}")
        print(f"   Buckets: {', '.join(gallery_manifest['buckets'])}")
        print(f"   Prefix: {gallery_manifest['prefix']}")
        
        return True
        
    except FileNotFoundError:
        print(f"✗ File not found: {INPUT_FILE}")
        print(f"   Make sure you're in the project root directory")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error parsing JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Convert Manifest for Gallery")
    print("=" * 60)
    print()
    
    if convert_manifest():
        print("\n✅ Success! Now copy to public folder:")
        print(f"   copy {OUTPUT_FILE} public\\{OUTPUT_FILE}")
        print(f"   firebase deploy --only hosting")
    else:
        print("\n❌ Conversion failed")
        sys.exit(1)
