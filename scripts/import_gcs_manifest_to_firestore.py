"""
Import GCS manifest to Firestore for viewer access
Creates image metadata records with train/test/folder information
Updated for Google Cloud Storage (GCS) instead of S3
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Initialize Firebase (if not already initialized)
    if not firebase_admin._apps:
        # Try to find service account key or use application default
        cred_path = Path('serviceAccountKey.json')
        if cred_path.exists():
            cred = credentials.Certificate(str(cred_path))
        else:
            # Use application default credentials
            cred = credentials.ApplicationDefault()
        
        firebase_admin.initialize_app(cred, {
            'projectId': 'hv-ecg'  # Change to your Firebase project ID
        })
    
    db = firestore.client()
    print("Firebase Firestore connected")
    
except ImportError:
    print("Error: firebase-admin not installed")
    print("Install with: pip install firebase-admin")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    print("Make sure you have Firebase Admin SDK configured")
    sys.exit(1)


def import_manifest(manifest_path: str, collection_name: str = 'kaggle_images'):
    """
    Import GCS manifest to Firestore
    
    Args:
        manifest_path: Path to manifest JSON file
        collection_name: Firestore collection name
    """
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print(f"Importing {len(manifest['images'])} images to Firestore...")
    print(f"Collection: {collection_name}")
    print(f"Storage: {manifest.get('storage_type', 'gcs')}")
    
    imported = 0
    errors = []
    
    for img in manifest['images']:
        try:
            # Create document with image metadata
            doc_id = img['filename'].replace('/', '_').replace('\\', '_')
            
            doc_data = {
                'filename': img['filename'],
                'full_path': img['full_path'],
                'gcs_bucket': img['gcs_bucket'],
                'gcs_path': img['gcs_path'],
                'gcs_url': img['gcs_url'],
                'gcs_public_url': img.get('gcs_public_url', ''),
                'size': img['size'],
                'size_formatted': img['size_formatted'],
                'is_train': img['is_train'],
                'is_test': img['is_test'],
                'folder': img['folder'],
                'competition': manifest['competition'],
                'source': 'kaggle',
                'storage_type': manifest.get('storage_type', 'gcs'),
                'imported_at': datetime.now(),
                'transfer_date': manifest['transfer_date'],
                'metadata': img['metadata']
            }
            
            # Save to Firestore
            db.collection(collection_name).document(doc_id).set(doc_data)
            imported += 1
            
            if imported % 100 == 0:
                print(f"  Imported {imported}/{len(manifest['images'])}...")
                
        except Exception as e:
            errors.append((img['filename'], str(e)))
            print(f"  Error importing {img['filename']}: {e}")
    
    print(f"\nImport complete: {imported}/{len(manifest['images'])} images")
    
    if errors:
        print(f"⚠️  Errors: {len(errors)}")
        for filename, error in errors[:10]:
            print(f"  - {filename}: {error}")
    
    # Create summary document
    summary_doc = {
        'competition': manifest['competition'],
        'total_images': len(manifest['images']),
        'train_count': sum(1 for img in manifest['images'] if img['is_train']),
        'test_count': sum(1 for img in manifest['images'] if img['is_test']),
        'transfer_date': manifest['transfer_date'],
        'import_date': datetime.now().isoformat(),
        'storage_type': manifest.get('storage_type', 'gcs'),
        'buckets_used': manifest.get('buckets_used', [])
    }
    
    db.collection('kaggle_transfers').document(manifest['competition']).set(summary_doc)
    
    return imported, errors


if __name__ == "__main__":
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else 'image_manifest_gcs.json'
    
    if not Path(manifest_path).exists():
        print(f"Error: Manifest file not found: {manifest_path}")
        print("Usage: python import_gcs_manifest_to_firestore.py [manifest.json]")
        sys.exit(1)
    
    print(f"Loading manifest from: {manifest_path}")
    imported, errors = import_manifest(manifest_path)
    
    print(f"\n✓ Firestore import complete!")
    print(f"  Collection: kaggle_images")
    print(f"  Documents: {imported}")
