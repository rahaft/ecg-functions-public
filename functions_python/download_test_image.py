"""
Download a sample ECG image from GCS for testing transformations
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    from google.cloud import storage
except ImportError:
    print("Error: google-cloud-storage not installed")
    print("Install with: pip install google-cloud-storage")
    sys.exit(1)

def download_sample_image():
    """Download a sample ECG image from GCS"""
    
    # Initialize GCS client
    storage_client = storage.Client(project='hv-ecg')
    
    # Try buckets in order
    buckets_to_try = [
        'ecg-competition-data-1',
        'ecg-competition-data-2',
        'ecg-competition-data-3',
        'ecg-competition-data-4',
        'ecg-competition-data-5'
    ]
    
    print("Searching for a sample ECG image in GCS buckets...")
    
    for bucket_name in buckets_to_try:
        try:
            bucket = storage_client.bucket(bucket_name)
            
            # List first few PNG files
            blobs = bucket.list_blobs(prefix='kaggle-data/physionet-ecg/', max_results=10)
            
            for blob in blobs:
                if blob.name.endswith('.png'):
                    print(f"\nFound image: {blob.name}")
                    print(f"Downloading from bucket: {bucket_name}...")
                    
                    # Download to current directory
                    filename = os.path.basename(blob.name)
                    local_path = filename
                    
                    blob.download_to_filename(local_path)
                    
                    print(f"✅ Downloaded: {local_path}")
                    print(f"   Size: {os.path.getsize(local_path) / 1024:.1f} KB")
                    print(f"\nYou can now test with:")
                    print(f"   python test_transformations.py {local_path}")
                    
                    return local_path
                    
        except Exception as e:
            print(f"  Could not access {bucket_name}: {e}")
            continue
    
    print("\n❌ No images found in GCS buckets")
    print("   Make sure buckets are accessible and contain images")
    return None

if __name__ == '__main__':
    image_path = download_sample_image()
    if image_path:
        print(f"\n✅ Ready to test! Run:")
        print(f"   python test_transformations.py {image_path}")
