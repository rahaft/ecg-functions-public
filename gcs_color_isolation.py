"""
GCS Color Isolation - Process images from Google Cloud Storage
==============================================================

This script:
1. Downloads images from GCS
2. Processes them locally (color isolation)
3. Uploads results back to GCS
4. Tracks all created files for easy deletion

Run locally with: python gcs_color_isolation.py
"""

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict
import tempfile

# ============================================
# Configuration
# ============================================

# GCS Settings
GCS_BUCKET = "hv-ecg-data"
GCS_SOURCE_FOLDER = "train"  # Where original images are
GCS_OUTPUT_FOLDER = "v6_color_split"  # Where to save processed images

# Local temp folder for processing
LOCAL_TEMP = tempfile.mkdtemp(prefix="ecg_color_")
print(f"Using temp folder: {LOCAL_TEMP}")

# Processing options
VERSION = "v6"
USE_ALL_METHODS = True
TEST_LIMIT = 10  # Start with 10 images for testing

# Minimum thresholds
MIN_ECG_PIXELS = 1000
MIN_GRID_PIXELS = 5000

# Track all created files for potential deletion
CREATED_FILES = []  # Will store GCS paths of all created files


# ============================================
# GCS Functions
# ============================================

def get_gcs_client():
    """Get authenticated GCS client."""
    try:
        from google.cloud import storage
        return storage.Client()
    except Exception as e:
        print(f"Error connecting to GCS: {e}")
        print("\nMake sure you have:")
        print("1. pip install google-cloud-storage")
        print("2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   Or run: gcloud auth application-default login")
        return None


def list_gcs_images(bucket_name, folder, limit=None):
    """List images in GCS bucket."""
    client = get_gcs_client()
    if not client:
        return []
    
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=f"{folder}/")
    
    images = []
    for blob in blobs:
        name = blob.name.lower()
        # Only get original images (not processed ones)
        if (name.endswith('.png') or name.endswith('.jpg')) and '--s-' not in name and '--sk-' not in name and '--original' not in name:
            images.append(blob.name)
            if limit and len(images) >= limit:
                break
    
    return images


def download_from_gcs(bucket_name, blob_path, local_path):
    """Download a file from GCS."""
    client = get_gcs_client()
    if not client:
        return False
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)
    return True


def upload_to_gcs(local_path, bucket_name, blob_path):
    """Upload a file to GCS and track it."""
    client = get_gcs_client()
    if not client:
        return None
    
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)
    
    # Track the file for potential deletion
    CREATED_FILES.append(blob_path)
    
    return f"gs://{bucket_name}/{blob_path}"


def delete_from_gcs(bucket_name, blob_paths):
    """Delete files from GCS."""
    client = get_gcs_client()
    if not client:
        return False
    
    bucket = client.bucket(bucket_name)
    deleted = []
    
    for blob_path in blob_paths:
        try:
            blob = bucket.blob(blob_path)
            blob.delete()
            deleted.append(blob_path)
            print(f"  Deleted: {blob_path}")
        except Exception as e:
            print(f"  Error deleting {blob_path}: {e}")
    
    return deleted


# ============================================
# Color Isolation Functions (same as before)
# ============================================

def detect_text_regions(image_bgr):
    """Detect text regions in the image."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    
    kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
    
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_h)
    horizontal = cv2.dilate(horizontal, kernel_h, iterations=2)
    
    vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_v)
    vertical = cv2.dilate(vertical, kernel_v, iterations=2)
    
    text_mask = cv2.bitwise_or(horizontal, vertical)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
    text_regions = np.zeros_like(gray)
    
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        aspect_ratio = w / max(h, 1)
        is_text = False
        
        if area < 5000 and area > 50:
            if aspect_ratio > 2 or aspect_ratio < 0.5:
                is_text = True
            img_h, img_w = gray.shape
            if y < img_h * 0.15 or y > img_h * 0.85:
                is_text = True
            if x < img_w * 0.1 or x > img_w * 0.9:
                is_text = True
        
        if is_text:
            text_regions[labels == i] = 255
    
    final_text_mask = cv2.bitwise_or(text_mask, text_regions)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    final_text_mask = cv2.dilate(final_text_mask, kernel, iterations=2)
    
    return final_text_mask


def calculate_red_quality_score(image_bgr):
    """RED score: % black pixels x 1000 (LOWER = better)"""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    black_pixels = np.sum(gray < 50)
    total_pixels = gray.size
    return int((black_pixels / total_pixels) * 100 * 1000)


def calculate_black_quality_score(image_bgr):
    """BLACK score: total black pixels (HIGHER = better)"""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return int(np.sum(gray < 50))


def isolate_ecg_opencv(image_bgr, remove_text=True):
    """Remove red grid, keep black ECG traces."""
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask_red1, mask_red2)
    
    lower_pink = np.array([0, 20, 150])
    upper_pink = np.array([20, 100, 255])
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    
    grid_mask = cv2.bitwise_or(red_mask, pink_mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grid_mask = cv2.dilate(grid_mask, kernel, iterations=1)
    
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    dark_mask = gray < 100
    non_grid_dark = np.logical_and(dark_mask, grid_mask == 0)
    
    result = np.ones_like(gray) * 255
    result[non_grid_dark] = gray[non_grid_dark]
    result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
    
    if remove_text:
        text_mask = detect_text_regions(image_bgr)
        result_bgr[text_mask > 0] = [255, 255, 255]
    
    return result_bgr, int(np.sum(non_grid_dark))


def isolate_grid_opencv(image_bgr):
    """Remove black ECG traces, keep red grid only."""
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    
    lower_red1 = np.array([0, 30, 30])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([165, 30, 30])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask_red1, mask_red2)
    
    lower_pink = np.array([0, 10, 150])
    upper_pink = np.array([25, 150, 255])
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    
    grid_mask = cv2.bitwise_or(red_mask, pink_mask)
    
    result = np.ones_like(image_bgr) * 255
    result[grid_mask > 0] = image_bgr[grid_mask > 0]
    
    return result, int(np.sum(grid_mask > 0))


def isolate_ecg_pillow(image_bgr, remove_text=True):
    """Remove red grid using Pillow channel splitting."""
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb)
    
    r, g, b = pil_image.split()
    r_array = np.array(r)
    g_array = np.array(g)
    b_array = np.array(b)
    
    red_dominant = (r_array > 120) & (r_array > g_array + 30) & (r_array > b_array + 30)
    pink = (r_array > 180) & (g_array > 100) & (b_array > 100) & (r_array > g_array)
    grid_mask = red_dominant | pink
    
    gray = np.array(pil_image.convert('L'))
    result = np.ones_like(gray) * 255
    dark_mask = gray < 120
    keep_mask = dark_mask & ~grid_mask
    result[keep_mask] = gray[keep_mask]
    
    result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
    
    if remove_text:
        text_mask = detect_text_regions(image_bgr)
        result_bgr[text_mask > 0] = [255, 255, 255]
    
    return result_bgr, int(np.sum(keep_mask))


def isolate_grid_pillow(image_bgr):
    """Keep only red grid using Pillow."""
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb)
    
    r, g, b = pil_image.split()
    r_array = np.array(r)
    g_array = np.array(g)
    b_array = np.array(b)
    
    red_dominant = (r_array > 100) & (r_array > g_array + 20) & (r_array > b_array + 20)
    pink = (r_array > 150) & (g_array > 80) & (b_array > 80) & (r_array > g_array)
    grid_mask = red_dominant | pink
    
    result = np.ones_like(image_bgr) * 255
    result[grid_mask] = image_bgr[grid_mask]
    
    return result, int(np.sum(grid_mask))


# ============================================
# Processing Functions
# ============================================

def generate_output_filename(original_filename, method, color_type, score, is_keeper=False):
    """Generate output filename."""
    base = os.path.splitext(os.path.basename(original_filename))[0]
    prefix = "--sk-" if is_keeper else "--s-"
    return f"{base}{prefix}{VERSION}-{method}-{color_type}-{score}.png"


def process_single_image(gcs_path, methods=['opencv', 'pillow']):
    """Process a single image from GCS."""
    filename = os.path.basename(gcs_path)
    base_name = os.path.splitext(filename)[0]
    
    # Download image
    local_path = os.path.join(LOCAL_TEMP, filename)
    print(f"  Downloading: {filename}")
    if not download_from_gcs(GCS_BUCKET, gcs_path, local_path):
        return None
    
    # Read image
    image = cv2.imread(local_path)
    if image is None:
        print(f"  Error: Could not read image")
        return None
    
    results = {
        'source': gcs_path,
        'filename': filename,
        'black_scores': {},
        'red_scores': {},
        'uploaded_files': []
    }
    
    # Upload original for comparison
    original_gcs_path = f"{GCS_OUTPUT_FOLDER}/{base_name}--original.png"
    upload_to_gcs(local_path, GCS_BUCKET, original_gcs_path)
    results['uploaded_files'].append(original_gcs_path)
    print(f"  Uploaded original: {base_name}--original.png")
    
    # Process with each method
    for method in methods:
        print(f"  Method: {method}")
        
        # ECG (black)
        if method == 'opencv':
            ecg_img, ecg_pixels = isolate_ecg_opencv(image)
            grid_img, grid_pixels = isolate_grid_opencv(image)
        else:  # pillow
            ecg_img, ecg_pixels = isolate_ecg_pillow(image)
            grid_img, grid_pixels = isolate_grid_pillow(image)
        
        # Calculate scores
        black_score = calculate_black_quality_score(ecg_img)
        red_score = calculate_red_quality_score(grid_img)
        
        results['black_scores'][method] = black_score
        results['red_scores'][method] = red_score
        
        print(f"    BLACK: {black_score:,} pixels | RED: {red_score} contamination")
        
        # Save and upload BLACK
        if ecg_pixels >= MIN_ECG_PIXELS:
            black_filename = generate_output_filename(filename, method, 'black', black_score)
            black_local = os.path.join(LOCAL_TEMP, black_filename)
            cv2.imwrite(black_local, ecg_img)
            
            black_gcs_path = f"{GCS_OUTPUT_FOLDER}/{black_filename}"
            upload_to_gcs(black_local, GCS_BUCKET, black_gcs_path)
            results['uploaded_files'].append(black_gcs_path)
            results[f'{method}_black_path'] = black_gcs_path
            results[f'{method}_black_img'] = ecg_img
        
        # Save and upload RED
        if grid_pixels >= MIN_GRID_PIXELS:
            red_filename = generate_output_filename(filename, method, 'red', red_score)
            red_local = os.path.join(LOCAL_TEMP, red_filename)
            cv2.imwrite(red_local, grid_img)
            
            red_gcs_path = f"{GCS_OUTPUT_FOLDER}/{red_filename}"
            upload_to_gcs(red_local, GCS_BUCKET, red_gcs_path)
            results['uploaded_files'].append(red_gcs_path)
            results[f'{method}_red_path'] = red_gcs_path
            results[f'{method}_red_img'] = grid_img
    
    # Select and upload KEEPERS
    if results['black_scores']:
        best_black = max(results['black_scores'], key=results['black_scores'].get)
        keeper_black_filename = generate_output_filename(filename, best_black, 'black', 
                                                         results['black_scores'][best_black], is_keeper=True)
        keeper_black_local = os.path.join(LOCAL_TEMP, keeper_black_filename)
        
        if f'{best_black}_black_img' in results:
            cv2.imwrite(keeper_black_local, results[f'{best_black}_black_img'])
            keeper_black_gcs = f"{GCS_OUTPUT_FOLDER}/{keeper_black_filename}"
            upload_to_gcs(keeper_black_local, GCS_BUCKET, keeper_black_gcs)
            results['uploaded_files'].append(keeper_black_gcs)
            print(f"  KEEPER BLACK: {keeper_black_filename}")
    
    if results['red_scores']:
        best_red = min(results['red_scores'], key=results['red_scores'].get)
        keeper_red_filename = generate_output_filename(filename, best_red, 'red',
                                                       results['red_scores'][best_red], is_keeper=True)
        keeper_red_local = os.path.join(LOCAL_TEMP, keeper_red_filename)
        
        if f'{best_red}_red_img' in results:
            cv2.imwrite(keeper_red_local, results[f'{best_red}_red_img'])
            keeper_red_gcs = f"{GCS_OUTPUT_FOLDER}/{keeper_red_filename}"
            upload_to_gcs(keeper_red_local, GCS_BUCKET, keeper_red_gcs)
            results['uploaded_files'].append(keeper_red_gcs)
            print(f"  KEEPER RED: {keeper_red_filename}")
    
    # Clean up temp images (remove from results to save memory)
    for key in list(results.keys()):
        if '_img' in key:
            del results[key]
    
    return results


# ============================================
# Main Functions
# ============================================

def main():
    """Main processing function."""
    print("=" * 60)
    print(f"GCS Color Isolation - {VERSION}")
    print("=" * 60)
    print(f"Bucket: {GCS_BUCKET}")
    print(f"Source folder: {GCS_SOURCE_FOLDER}")
    print(f"Output folder: {GCS_OUTPUT_FOLDER}")
    print(f"Test limit: {TEST_LIMIT}")
    print("=" * 60)
    
    # List images
    print("\nListing images in GCS...")
    images = list_gcs_images(GCS_BUCKET, GCS_SOURCE_FOLDER, limit=TEST_LIMIT)
    print(f"Found {len(images)} images to process")
    
    if not images:
        print("No images found!")
        return
    
    # Process images
    all_results = []
    for i, gcs_path in enumerate(images):
        print(f"\n[{i+1}/{len(images)}] {os.path.basename(gcs_path)}")
        result = process_single_image(gcs_path)
        if result:
            all_results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Images processed: {len(all_results)}")
    print(f"Total files created: {len(CREATED_FILES)}")
    
    # Save manifest of created files
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'version': VERSION,
        'bucket': GCS_BUCKET,
        'output_folder': GCS_OUTPUT_FOLDER,
        'created_files': CREATED_FILES,
        'results': all_results
    }
    
    manifest_path = os.path.join(LOCAL_TEMP, 'created_files_manifest.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Upload manifest
    manifest_gcs = f"{GCS_OUTPUT_FOLDER}/created_files_manifest.json"
    upload_to_gcs(manifest_path, GCS_BUCKET, manifest_gcs)
    
    print(f"\nManifest saved to: gs://{GCS_BUCKET}/{manifest_gcs}")
    print(f"Local temp folder: {LOCAL_TEMP}")
    
    return all_results


def delete_all_created_files():
    """Delete all files that were created in this session."""
    if not CREATED_FILES:
        print("No files to delete (CREATED_FILES is empty)")
        return
    
    print(f"\nDeleting {len(CREATED_FILES)} created files...")
    deleted = delete_from_gcs(GCS_BUCKET, CREATED_FILES)
    print(f"Deleted {len(deleted)} files")


def delete_files_from_manifest(manifest_path):
    """Delete files listed in a manifest JSON file."""
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    files_to_delete = manifest.get('created_files', [])
    print(f"Found {len(files_to_delete)} files in manifest")
    
    confirm = input("Delete these files? (yes/no): ")
    if confirm.lower() == 'yes':
        deleted = delete_from_gcs(manifest['bucket'], files_to_delete)
        print(f"Deleted {len(deleted)} files")
    else:
        print("Cancelled")


def delete_specific_files(file_patterns):
    """
    Delete files matching specific patterns from GCS.
    
    Example patterns:
    - "v6_color_split/*--s-*"  # All regular (non-keeper) files
    - "v6_color_split/*opencv*"  # All opencv files
    """
    client = get_gcs_client()
    if not client:
        return
    
    bucket = client.bucket(GCS_BUCKET)
    
    for pattern in file_patterns:
        folder = pattern.split('/')[0]
        blobs = bucket.list_blobs(prefix=f"{folder}/")
        
        matching = []
        for blob in blobs:
            # Simple pattern matching
            if '*' in pattern:
                parts = pattern.split('*')
                if all(part in blob.name for part in parts if part):
                    matching.append(blob.name)
            elif pattern in blob.name:
                matching.append(blob.name)
        
        print(f"Pattern '{pattern}' matches {len(matching)} files")
        for f in matching[:5]:
            print(f"  {f}")
        if len(matching) > 5:
            print(f"  ... and {len(matching) - 5} more")


# ============================================
# Run
# ============================================

if __name__ == "__main__":
    print("GCS Color Isolation Script")
    print("-" * 40)
    print("Commands:")
    print("  1. Process images (run main)")
    print("  2. Delete all created files")
    print("  3. Exit")
    print("-" * 40)
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == '1':
        results = main()
        
        # Ask about deletion
        print("\n" + "-" * 40)
        print("What would you like to do with the created files?")
        print("  k = Keep all files")
        print("  d = Delete all files")
        print("  r = Delete only regular files (keep --sk- keepers)")
        
        action = input("Enter choice (k/d/r): ").strip().lower()
        
        if action == 'd':
            delete_all_created_files()
        elif action == 'r':
            # Delete only non-keeper files
            regular_files = [f for f in CREATED_FILES if '--sk-' not in f and '--original' not in f]
            print(f"Deleting {len(regular_files)} regular files (keeping keepers and originals)...")
            delete_from_gcs(GCS_BUCKET, regular_files)
    
    elif choice == '2':
        manifest_path = input("Enter manifest path (or press Enter to delete session files): ").strip()
        if manifest_path:
            delete_files_from_manifest(manifest_path)
        else:
            delete_all_created_files()
    
    else:
        print("Exiting")
