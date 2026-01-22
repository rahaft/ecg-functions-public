"""
ECG Color Isolation - Kaggle Notebook
=====================================

This notebook processes ECG images to separate:
- Black ECG traces (remove red grid AND text)
- Red grid only (remove black traces)

Naming convention:
- Regular: {original_name}--s-{version}-{method}-{color}-{score}.png
- Keeper:  {original_name}--sk-{version}-{method}-{color}-{score}.png

SCORING:
- RED: % black pixels x 1000 (LOWER = better, less contamination)
- BLACK: total black pixel count (HIGHER = better, more ECG data)

Only the BEST images get the --sk- prefix:
- BLACK: method with HIGHEST pixel count
- RED: method with LOWEST contamination score

Run this in a Kaggle notebook with the ECG dataset attached.
"""

# ============================================
# CELL 1: Install dependencies and imports
# ============================================

import os
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import json
import shutil
from datetime import datetime
from collections import defaultdict

# Check for optional libraries
try:
    from skimage import color
    from skimage.color import rgb2hsv
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("scikit-image not available, using OpenCV and Pillow only")

# For GCS upload
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("google-cloud-storage not available. Install with: pip install google-cloud-storage")

print(f"OpenCV version: {cv2.__version__}")
print(f"scikit-image available: {SKIMAGE_AVAILABLE}")
print(f"GCS available: {GCS_AVAILABLE}")


# ============================================
# CELL 2: Configuration
# ============================================

# Kaggle dataset path (adjust based on your setup)
KAGGLE_INPUT_PATH = "/kaggle/input/physionet-ecg-image-digitization/train"

# Version - change this when you want a fresh run
VERSION = "v6"

# Output path - all images go to same folder
# Regular images: --s- prefix
# Best/keeper images: --sk- prefix
OUTPUT_PATH = f"/kaggle/working/{VERSION}_color_split"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# GCS Configuration (set these if uploading to GCS)
GCS_BUCKET = "hv-ecg-data"
GCS_FOLDER = "train"

# Processing options
USE_ALL_METHODS = True  # Try opencv, pillow, AND skimage on each image
SINGLE_METHOD = "opencv"  # Only used if USE_ALL_METHODS = False
OUTPUT_TYPE = "both"  # Options: "ecg" (black), "grid" (red), "both"

# Batch size for processing
BATCH_SIZE = 100

# TEST MODE: Set to a number to limit processing
TEST_LIMIT = 30  # Process first 30 images for testing!

# Minimum thresholds for saving
MIN_ECG_PIXELS = 1000
MIN_GRID_PIXELS = 5000

# Save behavior
SAVE_MONOTONE = True
DELETE_OLD_VERSIONS = True  # Delete images from previous versions at startup


# ============================================
# CELL 3: Cleanup Old Versions
# ============================================

def delete_old_version_images():
    """Delete images from previous versions (not matching current VERSION)."""
    working_dir = Path("/kaggle/working")
    
    if not working_dir.exists():
        return
    
    deleted_count = 0
    
    for item in working_dir.iterdir():
        if item.is_dir():
            if "_color_split" in item.name and VERSION not in item.name:
                print(f"Deleting old version folder: {item.name}")
                shutil.rmtree(item)
                deleted_count += 1
    
    if deleted_count > 0:
        print(f"Deleted {deleted_count} old version folders")
    else:
        print("No old version folders to delete")


# ============================================
# CELL 4: Text Detection and Removal
# ============================================

def detect_text_regions(image_bgr):
    """
    Detect text regions in the image using morphological operations.
    Text typically appears as small, dense clusters of dark pixels.
    """
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


def remove_text_from_black(image_bgr, text_mask):
    """Remove text regions from the black (ECG) image."""
    result = image_bgr.copy()
    result[text_mask > 0] = [255, 255, 255]
    return result


# ============================================
# CELL 5: Quality Score Functions
# ============================================

def calculate_red_quality_score(image_bgr):
    """
    Calculate quality score for RED (grid) isolation.
    Score = percentage of black pixels x 1000
    LOWER = better (less ECG contamination)
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    black_threshold = 50
    black_pixels = np.sum(gray < black_threshold)
    total_pixels = gray.size
    black_percentage = (black_pixels / total_pixels) * 100
    score = int(black_percentage * 1000)
    return score


def calculate_black_quality_score(image_bgr):
    """
    Calculate quality score for BLACK (ECG) isolation.
    Score = total count of black pixels
    HIGHER = better (more ECG data captured)
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    black_threshold = 50
    black_pixel_count = int(np.sum(gray < black_threshold))
    return black_pixel_count


# ============================================
# CELL 6: Color Isolation Functions
# ============================================

def isolate_ecg_opencv(image_bgr, remove_text=True):
    """Remove red grid, keep black ECG traces using OpenCV."""
    metrics = {'method': 'opencv', 'type': 'ecg'}
    
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
    
    dark_threshold = 100
    dark_mask = gray < dark_threshold
    non_grid_dark = np.logical_and(dark_mask, grid_mask == 0)
    
    result = np.ones_like(gray) * 255
    result[non_grid_dark] = gray[non_grid_dark]
    
    result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
    
    if remove_text:
        text_mask = detect_text_regions(image_bgr)
        result_bgr = remove_text_from_black(result_bgr, text_mask)
        metrics['text_pixels_removed'] = int(np.sum(text_mask > 0))
    
    metrics['pixels_removed'] = int(np.sum(grid_mask > 0))
    metrics['pixels_kept'] = int(np.sum(non_grid_dark))
    
    return result_bgr, metrics


def isolate_grid_opencv(image_bgr):
    """Remove black ECG traces, keep red grid only using OpenCV."""
    metrics = {'method': 'opencv', 'type': 'grid'}
    
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
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    grid_mask = cv2.morphologyEx(grid_mask, cv2.MORPH_CLOSE, kernel)
    
    result = np.ones_like(image_bgr) * 255
    result[grid_mask > 0] = image_bgr[grid_mask > 0]
    
    metrics['pixels_kept'] = int(np.sum(grid_mask > 0))
    
    return result, metrics


def isolate_ecg_pillow(image_bgr, remove_text=True):
    """Remove red grid using Pillow channel splitting."""
    metrics = {'method': 'pillow', 'type': 'ecg'}
    
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
        result_bgr = remove_text_from_black(result_bgr, text_mask)
        metrics['text_pixels_removed'] = int(np.sum(text_mask > 0))
    
    metrics['pixels_removed'] = int(np.sum(grid_mask))
    metrics['pixels_kept'] = int(np.sum(keep_mask))
    
    return result_bgr, metrics


def isolate_grid_pillow(image_bgr):
    """Keep only red grid using Pillow."""
    metrics = {'method': 'pillow', 'type': 'grid'}
    
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
    
    metrics['pixels_kept'] = int(np.sum(grid_mask))
    
    return result, metrics


def isolate_ecg_skimage(image_bgr, remove_text=True):
    """Remove red grid using scikit-image."""
    if not SKIMAGE_AVAILABLE:
        raise ImportError("scikit-image not available")
    
    from skimage import morphology
    
    metrics = {'method': 'skimage', 'type': 'ecg'}
    
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    rgb_float = rgb.astype(np.float64) / 255.0
    
    hsv = rgb2hsv(rgb_float)
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    red_hue = (h < 0.08) | (h > 0.92)
    saturated = s > 0.15
    red_mask = red_hue & saturated
    
    red_mask = morphology.dilation(red_mask, morphology.disk(2))
    
    gray = color.rgb2gray(rgb_float)
    
    dark_mask = gray < 0.5
    keep_mask = dark_mask & ~red_mask
    
    result = np.ones_like(gray)
    result[keep_mask] = gray[keep_mask]
    
    result_uint8 = (result * 255).astype(np.uint8)
    result_bgr = cv2.cvtColor(result_uint8, cv2.COLOR_GRAY2BGR)
    
    if remove_text:
        text_mask = detect_text_regions(image_bgr)
        result_bgr = remove_text_from_black(result_bgr, text_mask)
        metrics['text_pixels_removed'] = int(np.sum(text_mask > 0))
    
    metrics['pixels_removed'] = int(np.sum(red_mask))
    metrics['pixels_kept'] = int(np.sum(keep_mask))
    
    return result_bgr, metrics


def isolate_grid_skimage(image_bgr):
    """Keep only red grid using scikit-image."""
    if not SKIMAGE_AVAILABLE:
        raise ImportError("scikit-image not available")
    
    metrics = {'method': 'skimage', 'type': 'grid'}
    
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    rgb_float = rgb.astype(np.float64) / 255.0
    
    hsv = rgb2hsv(rgb_float)
    h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    
    red_hue = (h < 0.1) | (h > 0.9)
    has_color = s > 0.1
    grid_mask = red_hue & has_color
    
    result = np.ones_like(image_bgr) * 255
    result[grid_mask] = image_bgr[grid_mask]
    
    metrics['pixels_kept'] = int(np.sum(grid_mask))
    
    return result, metrics


# ============================================
# CELL 7: Processing Functions
# ============================================

METHOD_NAMES = {'opencv': 'opencv', 'pillow': 'pillow', 'skimage': 'skimage'}


def process_image(image_path, method='opencv', output_type='both'):
    """Process a single image for color isolation."""
    image = cv2.imread(str(image_path))
    if image is None:
        return {'success': False, 'error': f'Could not read image: {image_path}'}
    
    results = {'success': True, 'outputs': {}}
    
    try:
        if output_type in ['ecg', 'both']:
            if method == 'opencv':
                ecg_img, ecg_metrics = isolate_ecg_opencv(image, remove_text=True)
            elif method == 'pillow':
                ecg_img, ecg_metrics = isolate_ecg_pillow(image, remove_text=True)
            elif method == 'skimage':
                ecg_img, ecg_metrics = isolate_ecg_skimage(image, remove_text=True)
            results['outputs']['ecg'] = {'image': ecg_img, 'metrics': ecg_metrics}
        
        if output_type in ['grid', 'both']:
            if method == 'opencv':
                grid_img, grid_metrics = isolate_grid_opencv(image)
            elif method == 'pillow':
                grid_img, grid_metrics = isolate_grid_pillow(image)
            elif method == 'skimage':
                grid_img, grid_metrics = isolate_grid_skimage(image)
            results['outputs']['grid'] = {'image': grid_img, 'metrics': grid_metrics}
            
    except Exception as e:
        results['success'] = False
        results['error'] = str(e)
    
    return results


def generate_output_filename(original_filename, method, color_type, score=None, is_keeper=False):
    """
    Generate output filename with version and quality score.
    
    Format: 
    - Regular: {original_name}--s-{version}-{method}-{color}-{score}.png
    - Keeper:  {original_name}--sk-{version}-{method}-{color}-{score}.png
    
    The --sk- prefix indicates this is the BEST version to keep.
    """
    base = os.path.splitext(original_filename)[0]
    method_name = METHOD_NAMES.get(method, method)
    
    # Use --sk- for keeper images, --s- for regular
    prefix = "--sk-" if is_keeper else "--s-"
    
    if score is not None:
        return f"{base}{prefix}{VERSION}-{method_name}-{color_type}-{score}.png"
    else:
        return f"{base}{prefix}{VERSION}-{method_name}-{color_type}.png"


# ============================================
# CELL 8: Batch Processing with Best Selection
# ============================================

def find_ecg_images(input_path, extensions=['.png', '.jpg', '.jpeg']):
    """Find all ORIGINAL ECG images in the input directory."""
    images = []
    input_path = Path(input_path)
    
    for ext in extensions:
        images.extend(input_path.rglob(f'*{ext}'))
        images.extend(input_path.rglob(f'*{ext.upper()}'))
    
    filtered = []
    for img in images:
        filename = img.name
        filepath = str(img)
        
        if '/kaggle/working/' in filepath:
            continue
        if '--s-' in filename or '--sk-' in filename:
            continue
        if any(f'-{s}0' in filename for s in ['o', 'p', 's']):
            continue
        
        filtered.append(img)
    
    print(f"   Found {len(filtered)} original images (filtered from {len(images)} total)")
    return sorted(filtered)


def process_single_image_all_methods(img_path, methods, output_type='both'):
    """
    Process a single image with all methods.
    Saves ALL versions with --s- prefix, then saves BEST with --sk- prefix.
    Also copies the original image for comparison.
    """
    filename = img_path.name
    all_results = {
        'source': str(img_path), 
        'source_filename': filename, 
        'methods': {},
        'black_scores': {},
        'red_scores': {}
    }
    
    # Copy original image for comparison
    original_copy_name = f"{os.path.splitext(filename)[0]}--original.png"
    original_copy_path = os.path.join(OUTPUT_PATH, original_copy_name)
    original_image = cv2.imread(str(img_path))
    if original_image is not None:
        cv2.imwrite(original_copy_path, original_image)
        print(f"    Original copied: {original_copy_name}")
    
    for method in methods:
        if method == 'skimage' and not SKIMAGE_AVAILABLE:
            print(f"    Skipping {method} (not installed)")
            continue
            
        print(f"    Method: {method}")
        
        result = process_image(img_path, method=method, output_type=output_type)
        
        if result['success']:
            saved_files = []
            
            for out_type, out_data in result['outputs'].items():
                metrics = out_data['metrics']
                pixels_kept = metrics.get('pixels_kept', 0)
                output_image = out_data['image']
                
                if out_type == 'ecg':
                    min_pixels = MIN_ECG_PIXELS
                    color_name = "black"
                    display_name = "BLACK (ECG traces)"
                else:
                    min_pixels = MIN_GRID_PIXELS
                    color_name = "red"
                    display_name = "RED (grid)"
                
                print(f"       {display_name}: {pixels_kept:,} pixels")
                
                if pixels_kept < min_pixels:
                    if SAVE_MONOTONE:
                        color_type = "monotone"
                        print(f"       Low separation - saving as monotone")
                    else:
                        print(f"       Skipping - below threshold")
                        continue
                else:
                    color_type = color_name
                
                # Calculate quality score
                if color_type == "red":
                    score = calculate_red_quality_score(output_image)
                    all_results['red_scores'][method] = score
                    print(f"       Quality: {score} (LOWER = better)")
                elif color_type == "black":
                    score = calculate_black_quality_score(output_image)
                    all_results['black_scores'][method] = score
                    print(f"       Quality: {score:,} pixels (HIGHER = better)")
                else:
                    score = 0
                
                # Save to output folder with --s- naming (regular)
                out_filename = generate_output_filename(filename, method, color_type, score, is_keeper=False)
                out_filepath = os.path.join(OUTPUT_PATH, out_filename)
                
                cv2.imwrite(out_filepath, out_data['image'])
                saved_files.append({
                    'filename': out_filename,
                    'path': out_filepath,
                    'type': out_type,
                    'color': color_type,
                    'score': score,
                    'method': method,
                    'image': out_data['image'],
                    'metrics': metrics
                })
                
                print(f"       Saved: {out_filename}")
            
            all_results['methods'][method] = {
                'success': True,
                'saved_files': saved_files
            }
        else:
            print(f"       Error: {result.get('error', 'Unknown')}")
            all_results['methods'][method] = {
                'success': False,
                'error': result.get('error')
            }
    
    return all_results


def select_and_keep_best(all_results):
    """
    Select the best black and red images and save with --sk- prefix.
    - BLACK: method with HIGHEST pixel count
    - RED: method with LOWEST contamination score
    
    Both versions are kept in the same folder:
    - Regular: --s- prefix (all methods)
    - Keeper: --sk- prefix (best only)
    """
    kept_files = []
    source_filename = all_results.get('source_filename', '')
    
    # Find best BLACK (highest score)
    if all_results['black_scores']:
        best_black_method = max(all_results['black_scores'], key=all_results['black_scores'].get)
        best_black_score = all_results['black_scores'][best_black_method]
        print(f"    BEST BLACK: {best_black_method} (score: {best_black_score:,})")
        
        for method, method_result in all_results['methods'].items():
            if method == best_black_method and method_result.get('success'):
                for saved in method_result.get('saved_files', []):
                    if saved.get('color') == 'black' and 'image' in saved:
                        keeper_filename = generate_output_filename(
                            source_filename, method, 'black', saved['score'], is_keeper=True
                        )
                        keeper_path = os.path.join(OUTPUT_PATH, keeper_filename)
                        cv2.imwrite(keeper_path, saved['image'])
                        kept_files.append({
                            'filename': keeper_filename, 
                            'type': 'black', 
                            'method': method,
                            'score': saved['score']
                        })
                        print(f"    KEEPER: {keeper_filename}")
    
    # Find best RED (lowest score)
    if all_results['red_scores']:
        best_red_method = min(all_results['red_scores'], key=all_results['red_scores'].get)
        best_red_score = all_results['red_scores'][best_red_method]
        print(f"    BEST RED: {best_red_method} (score: {best_red_score})")
        
        for method, method_result in all_results['methods'].items():
            if method == best_red_method and method_result.get('success'):
                for saved in method_result.get('saved_files', []):
                    if saved.get('color') == 'red' and 'image' in saved:
                        keeper_filename = generate_output_filename(
                            source_filename, method, 'red', saved['score'], is_keeper=True
                        )
                        keeper_path = os.path.join(OUTPUT_PATH, keeper_filename)
                        cv2.imwrite(keeper_path, saved['image'])
                        kept_files.append({
                            'filename': keeper_filename, 
                            'type': 'red', 
                            'method': method,
                            'score': saved['score']
                        })
                        print(f"    KEEPER: {keeper_filename}")
    
    return kept_files


def process_batch(images, methods=None, output_type='both'):
    """Process a batch of images, saving all versions and marking best as keepers."""
    if methods is None:
        if USE_ALL_METHODS:
            methods = ['opencv', 'pillow', 'skimage']
        else:
            methods = [SINGLE_METHOD]
    
    results = []
    all_kept = []
    
    print(f"\nProcessing {len(images)} images with methods: {methods}")
    print(f"   Output folder: {OUTPUT_PATH}")
    print("=" * 60)
    
    for i, img_path in enumerate(images):
        filename = img_path.name
        print(f"\n[{i+1}/{len(images)}] {filename}")
        
        result = process_single_image_all_methods(img_path, methods=methods, output_type=output_type)
        
        print(f"\n    --- Selecting best ---")
        kept = select_and_keep_best(result)
        result['kept_files'] = kept
        all_kept.extend(kept)
        
        results.append(result)
    
    return results, all_kept


# ============================================
# CELL 9: Main Execution
# ============================================

def main():
    """Main processing function."""
    if USE_ALL_METHODS:
        methods = ['opencv', 'pillow', 'skimage']
        methods_str = "ALL (opencv, pillow, skimage)"
    else:
        methods = [SINGLE_METHOD]
        methods_str = SINGLE_METHOD
    
    print("=" * 60)
    print(f"ECG Color Isolation Processing - {VERSION}")
    print("=" * 60)
    print(f"Version: {VERSION}")
    print(f"Input path: {KAGGLE_INPUT_PATH}")
    print(f"Output folder: {OUTPUT_PATH}")
    print(f"Methods: {methods_str}")
    print(f"Test limit: {TEST_LIMIT if TEST_LIMIT else 'None (all images)'}")
    print("=" * 60)
    print("\nNaming convention:")
    print("  --s-  = all versions (regular)")
    print("  --sk- = best version (keeper)")
    
    # Delete old versions
    if DELETE_OLD_VERSIONS:
        print("\nChecking for old version folders...")
        delete_old_version_images()
    
    # Find images
    print("\nFinding images...")
    images = find_ecg_images(KAGGLE_INPUT_PATH)
    total_found = len(images)
    
    if TEST_LIMIT and TEST_LIMIT > 0:
        images = images[:TEST_LIMIT]
        print(f"TEST MODE: Processing only first {len(images)} images")
    
    if len(images) == 0:
        print("No images found! Check the input path.")
        return
    
    # Process all images
    all_results, all_kept = process_batch(images, methods=methods, output_type=OUTPUT_TYPE)
    
    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Images processed: {len(all_results)}")
    print(f"\nFiles kept (--sk- keepers): {len(all_kept)}")
    
    black_kept = sum(1 for k in all_kept if k['type'] == 'black')
    red_kept = sum(1 for k in all_kept if k['type'] == 'red')
    print(f"   BLACK (ECG): {black_kept}")
    print(f"   RED (Grid): {red_kept}")
    
    method_counts = defaultdict(int)
    for k in all_kept:
        method_counts[k['method']] += 1
    print(f"\n   By winning method:")
    for method, count in sorted(method_counts.items()):
        print(f"      {method}: {count}")
    
    print(f"\nOutput folder: {OUTPUT_PATH}")
    
    # Count total files
    output_path = Path(OUTPUT_PATH)
    all_files = list(output_path.glob("*.png"))
    keeper_files = [f for f in all_files if '--sk-' in f.name]
    regular_files = [f for f in all_files if '--s-' in f.name and '--sk-' not in f.name]
    
    print(f"\nTotal files saved:")
    print(f"   Regular (--s-): {len(regular_files)}")
    print(f"   Keepers (--sk-): {len(keeper_files)}")
    
    # Save manifest
    manifest_path = os.path.join(OUTPUT_PATH, "manifest.json")
    with open(manifest_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'version': VERSION,
            'methods': methods,
            'total_images': len(all_results),
            'kept_files': all_kept,
            'method_wins': dict(method_counts)
        }, f, indent=2, default=str)
    print(f"\nManifest saved: {manifest_path}")
    
    if TEST_LIMIT and TEST_LIMIT > 0:
        print(f"\nThis was a TEST RUN with {TEST_LIMIT} images.")
        print(f"Set TEST_LIMIT = None to process all {total_found} images.")
    
    return all_results, all_kept


# ============================================
# CELL 10: Run Everything
# ============================================

if __name__ == "__main__":
    print("Starting ECG Color Isolation...")
    results, kept = main()
    
    # List keeper files
    print("\n\n" + "="*60)
    print("KEEPER FILES (--sk- prefix)")
    print("="*60)
    output_path = Path(OUTPUT_PATH)
    if output_path.exists():
        keeper_files = sorted([f for f in output_path.glob("*.png") if '--sk-' in f.name])
        for f in keeper_files[:20]:
            print(f"  {f.name}")
        if len(keeper_files) > 20:
            print(f"  ... and {len(keeper_files) - 20} more")
