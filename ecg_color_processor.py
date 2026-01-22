"""
ECG Color Processor - Unified Multi-Mode Script
================================================

This script runs in THREE modes:
  1. KAGGLE   - Runs on Kaggle with no modifications (uses Kaggle input paths)
  2. CLOUD    - Downloads from GCS, processes, uploads results back to GCS
  3. GROUP    - Test specific image groups by prefix (local or cloud)

CONFIGURATION:
  Change the MODE variable below to switch between modes.
  
KAGGLE USAGE:
  1. Copy this file to a Kaggle notebook
  2. Set MODE = "KAGGLE"
  3. Run - it will automatically find the competition dataset

LOCAL TESTING:
  1. Set MODE = "CLOUD" or "GROUP"
  2. Configure GCS settings below
  3. Run: python ecg_color_processor.py

Author: HV-ECG Team
Version: 7.0
Last Updated: January 2026
"""

import os
import sys
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict
import tempfile
import random

# Set GCS credentials if service account key exists
SERVICE_ACCOUNT_PATH = r"C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"
if os.path.exists(SERVICE_ACCOUNT_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH

# ============================================================================
#                           MODE CONFIGURATION
# ============================================================================
# Change this to switch between modes:
#   "KAGGLE" - Run on Kaggle (no internet, uses local Kaggle paths)
#   "CLOUD"  - Download from GCS, process all, upload results
#   "GROUP"  - Process specific image groups by prefix (from GCS)
#   "LOCAL"  - Process local files (no GCS needed) - for testing

MODE = "LOCAL"  # <-- CHANGE THIS TO SWITCH MODES

# ============================================================================
#                         LOCAL MODE CONFIGURATION
# ============================================================================
# These settings are used when MODE = "LOCAL"
# Input and output folder for local processing

LOCAL_INPUT_FOLDER = r"D:\Gauntlet2\hv-ecg\red black sep photos"
LOCAL_OUTPUT_FOLDER = r"D:\Gauntlet2\hv-ecg\red black sep photos"

# ============================================================================
#                         KAGGLE CONFIGURATION
# ============================================================================
# These settings are used when MODE = "KAGGLE"

KAGGLE_INPUT_PATH = "/kaggle/input/physionet-ecg-image-digitization"
KAGGLE_OUTPUT_PATH = "/kaggle/working"

# ============================================================================
#                         CLOUD CONFIGURATION
# ============================================================================
# These settings are used when MODE = "CLOUD" or "GROUP"

# Available buckets: ecg-competition-data-1 through ecg-competition-data-5
GCS_BUCKET = "ecg-competition-data-1"
GCS_SOURCE_FOLDER = "kaggle-data/physionet-ecg/train"  # Path to training images
GCS_OUTPUT_FOLDER = "v7_color_split"  # Where to save processed images (if uploading)

# ============================================================================
#                         GROUP CONFIGURATION
# ============================================================================
# These settings are used when MODE = "GROUP"
# Image groups are identified by their prefix (the number before the first dash)
# Example: "1006427285" groups images like 1006427285-0001.png, 1006427285-0002.png, etc.

# Preset array of known image group prefixes (278 groups from GCS scan)
IMAGE_GROUP_PREFIXES = [
    "1006427285", "1006867983", "1012423188", "10140238", "1015663939", "102150619",
    "1026034238", "1041099777", "104573050", "1048962695", "1052007218", "1053922973",
    "1059602762", "1063816858", "106482869", "1067371646", "1067975047", "1068062585",
    "1072767337", "1079294623", "1084993373", "108599929", "1086830824", "1091894701",
    "1094825522", "1100434086", "1103133923", "1103158012", "1124135100", "112870634",
    "1135737846", "1142668792", "1146155934", "1147589496", "1151562032", "1154001412",
    "1154813853", "1158372875", "1163641242", "1173521301", "1174117563", "1177153463",
    "1178181553", "1183949786", "11842146", "1189828070", "1191130935", "1195437044",
    "119693645", "1197069178", "1199125619", "1209416227", "121471389", "1219936451",
    "1220748004", "1223595426", "1228736690", "1254751446", "1257259783", "1259907878",
    "1274262621", "1277179302", "1278116713", "1280609341", "1281093472", "1289824484",
    "129883643", "1306725887", "1310031403", "1312364803", "133948617", "136433453",
    "1364705568", "136524867", "1369067427", "1375500898", "1376451566", "1380849732",
    "1381006600", "1382137960", "1385441565", "1386861857", "1387453142", "1395556771",
    "1395637987", "1397514070", "1402030662", "1404687891", "1411350094", "1419593015",
    "1420515841", "1421059632", "1422666301", "142408315", "143477987", "1436234058",
    "1441250561", "1441897956", "1445349505", "1446634391", "144746082", "1449491391",
    "145098200", "1451074124", "145375843", "145399852", "1457768453", "1467515776",
    "147393955", "1475354244", "1481447856", "1484649389", "1484831977", "1490220713",
    "1492606769", "1502182655", "1502655579", "1503423095", "1505370821", "1509005816",
    "1512936796", "1522477000", "1524001991", "1531629157", "1533451101", "1536586741",
    "1539510874", "1542217251", "1553847883", "1555455483", "1556112478", "1557988993",
    "1560009706", "1561472702", "1562777197", "157249266", "1587099637", "1589810571",
    "1590643291", "1593926574", "1602385852", "1617515072", "1618780264", "1623613765",
    "162622667", "1626620456", "162686318", "1630401449", "1632590593", "1638509393",
    "1638532514", "1639217796", "1643754023", "1644219523", "1649759478", "1651876816",
    "1653260624", "1657128463", "1659921138", "1661642513", "1662993511", "1665441750",
    "1668094577", "1670304152", "1671648942", "1673456778", "1678324396", "168239620",
    "1683970273", "1692881983", "1696396696", "1698943335", "170158778", "1709636457",
    "1717124873", "1722454310", "1732081043", "1734729516", "1736488789", "1739475663",
    "1742556603", "1746570786", "1752267607", "1762299662", "1766417838", "1769470316",
    "1771293531", "1774595133", "1774656418", "1779646665", "1783318297", "1783777908",
    "1787792287", "1789763174", "1789983060", "1798516005", "1801481487", "181086745",
    "1815763003", "1815848373", "1818829830", "1833976046", "1841461559", "1849741174",
    "185534667", "1856029567", "1857740870", "1868006986", "1875329380", "1881229866",
    "1883137811", "1886812982", "1889366355", "1890954897", "1892490537", "1893309127",
    "1900639354", "190186115", "19030958", "1903158236", "1907398397", "1919286802",
    "1922153793", "1922265034", "1931150025", "1933191200", "1938036943", "194732810",
    "1948581413", "1949321289", "1951244635", "1953140023", "19585145", "1962423499",
    "1972793559", "197560770", "198290386", "1987857200", "1993778600", "1998779717",
    "2002854502", "2006667321", "2008728390", "2013781946", "2021850894", "2022371381",
    "2023163309", "2023794418", "202594271", "202613567", "2036251685", "2040854068",
    "2042290760", "2042532735", "2043481531", "2044379808", "2054044752", "2055953391",
    "2058553070", "2059782427", "2061343120", "2062750047", "2063154718", "2064004115",
    "2069796557", "2080106037", "2082219639", "2084535875", "2089312114", "2092320860",
    "2101175952", "2110921177", "2112146939", "2114009967", "2114049422", "2114687381",
    "2125192882", "212782370",
]

# Group selection options:
GROUP_SELECTION_MODE = "RANGE"  # "RANGE", "RANDOM", or "LIST"
GROUP_RANGE_START = 0           # For RANGE: start index (0-based)
GROUP_RANGE_END = 3             # For RANGE: end index (exclusive), so 0-3 = first 3 groups
GROUP_RANDOM_COUNT = 3          # For RANDOM: how many random groups to select
GROUP_LIST = [0, 2, 4]          # For LIST: specific indices to process

# ============================================================================
#                    ECG CALIBRATION ASSUMPTIONS
# ============================================================================
# Standard ECG paper specifications (these are the assumptions we validate)

ECG_ASSUMPTIONS = {
    # Grid specifications
    "grid_small_square_mm": 1.0,        # Each small square = 1mm x 1mm
    "grid_large_square_mm": 5.0,        # Each large square = 5mm x 5mm (5 small squares)
    
    # Voltage (vertical) calibration - Y axis
    "mv_per_10mm": 1.0,                 # Standard: 1mV = 10mm (10 small squares)
    "mv_per_small_square": 0.1,         # 0.1mV per 1mm square
    "mv_per_large_square": 0.5,         # 0.5mV per 5mm large square
    
    # Time (horizontal) calibration - X axis  
    "paper_speed_mm_per_sec": 25.0,     # Standard: 25mm/s
    "ms_per_small_square": 40.0,        # 40ms per 1mm (at 25mm/s)
    "ms_per_large_square": 200.0,       # 200ms per 5mm (at 25mm/s)
    
    # Alternative paper speeds (some ECGs use these)
    "alt_paper_speeds": [50.0, 12.5],   # 50mm/s or 12.5mm/s alternatives
    
    # Calibration pulse (reference marker)
    "calibration_pulse_mv": 1.0,        # 1mV standard calibration pulse
    "calibration_pulse_width_ms": 200,  # Usually 200ms wide
    
    # Expected image characteristics
    "expected_dpi_range": (150, 600),   # Typical scan DPI range
    "grid_color": "red/pink",           # Most common grid color
    "trace_color": "black",             # Most common trace color
}

# ============================================================================
#                         PROCESSING CONFIGURATION
# ============================================================================

VERSION = "v7"
USE_ALL_METHODS = True          # Process with all methods (opencv, pillow, skimage)
METHODS = ['opencv', 'pillow']  # Methods to use (add 'skimage' if available)

# Quality thresholds
MIN_ECG_PIXELS = 1000           # Minimum black pixels to save ECG image
MIN_GRID_PIXELS = 5000          # Minimum grid pixels to save grid image

# Color detection thresholds
RED_THRESHOLD_PERCENT = 1.0     # Minimum % of red pixels to consider "has red"
BLACK_THRESHOLD_PERCENT = 0.5   # Minimum % of black pixels to consider "has black"

# Text removal
REMOVE_TEXT = True              # Remove text from ECG (black) images

# File management
DELETE_OLD_VERSIONS = True      # Delete output from previous versions
SAVE_ORIGINALS = True           # Copy original image to output folder
GENERATE_ANALYSIS_MD = True     # Generate .md analysis file for each image

# Test limits
TEST_LIMIT = None               # Set to number to limit images (None = process all)

# Track created files for deletion (with metadata)
CREATED_FILES = []              # List of {'path': str, 'type': str, 'timestamp': str}

# ============================================================================
#                         ENVIRONMENT DETECTION
# ============================================================================

def detect_environment():
    """Detect if running on Kaggle or locally."""
    if os.path.exists("/kaggle"):
        return "KAGGLE"
    return "LOCAL"

ENVIRONMENT = detect_environment()
print(f"Environment detected: {ENVIRONMENT}")
print(f"Mode configured: {MODE}")

# Local temp folder for processing (only used in CLOUD/GROUP modes)
if ENVIRONMENT == "LOCAL":
    LOCAL_TEMP = tempfile.mkdtemp(prefix="ecg_color_")
    print(f"Using temp folder: {LOCAL_TEMP}")
else:
    LOCAL_TEMP = KAGGLE_OUTPUT_PATH

# ============================================================================
#                         FILE TRACKING
# ============================================================================

def track_file(path, file_type="image"):
    """Track a created file with metadata for later deletion."""
    CREATED_FILES.append({
        'path': path,
        'type': file_type,
        'timestamp': datetime.now().isoformat(),
        'version': VERSION
    })

def get_tracked_files_by_type(file_type=None):
    """Get tracked files, optionally filtered by type."""
    if file_type:
        return [f for f in CREATED_FILES if f['type'] == file_type]
    return CREATED_FILES

# ============================================================================
#                         GCS FUNCTIONS (CLOUD/GROUP MODES)
# ============================================================================

def get_gcs_client():
    """Get authenticated GCS client."""
    if MODE == "KAGGLE":
        return None
    try:
        from google.cloud import storage
        return storage.Client()
    except ImportError:
        print("Warning: google-cloud-storage not installed")
        print("Run: pip install google-cloud-storage")
        return None
    except Exception as e:
        print(f"Error connecting to GCS: {e}")
        return None


def list_gcs_images(bucket_name, folder, prefix_filter=None, limit=None):
    """List images in GCS bucket, optionally filtered by prefix."""
    client = get_gcs_client()
    if not client:
        return []
    
    bucket = client.bucket(bucket_name)
    
    images = []
    
    # If prefix filter specified, search in each prefix's subfolder
    if prefix_filter:
        for prefix in prefix_filter:
            # Images are in subfolders: folder/prefix/prefix-XXXX.png
            search_path = f"{folder}/{prefix}/" if folder else f"{prefix}/"
            print(f"  Searching: {search_path}")
            
            blobs = bucket.list_blobs(prefix=search_path)
            for blob in blobs:
                name = blob.name
                basename = os.path.basename(name).lower()
                
                # Skip processed images
                if '--s-' in basename or '--sk-' in basename or '--original' in basename:
                    continue
                
                # Check file extension
                if basename.endswith('.png') or basename.endswith('.jpg') or basename.endswith('.jpeg'):
                    images.append(blob.name)
                    if limit and len(images) >= limit:
                        return images
    else:
        # No filter - list all images in folder
        search_path = f"{folder}/" if folder else ""
        blobs = bucket.list_blobs(prefix=search_path)
        
        for blob in blobs:
            name = blob.name
            basename = os.path.basename(name).lower()
            
            # Skip processed images and analysis files
            if '--s-' in basename or '--sk-' in basename or '--original' in basename:
                continue
            if basename.endswith('.md') or basename.endswith('.json'):
                continue
            
            # Check file extension
            if basename.endswith('.png') or basename.endswith('.jpg') or basename.endswith('.jpeg'):
                images.append(blob.name)
                if limit and len(images) >= limit:
                    break
    
    return images


def download_from_gcs(bucket_name, blob_path, local_path):
    """Download a file from GCS."""
    import time
    client = get_gcs_client()
    if not client:
        return False
    
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        # Get file size for progress
        blob.reload()
        size_mb = blob.size / (1024 * 1024) if blob.size else 0
        
        print(f"  Downloading ({size_mb:.1f} MB)...", end=" ", flush=True)
        t0 = time.time()
        blob.download_to_filename(local_path)
        elapsed = time.time() - t0
        speed = size_mb / elapsed if elapsed > 0 else 0
        print(f"OK ({elapsed:.1f}s, {speed:.1f} MB/s)")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def upload_to_gcs(local_path, bucket_name, blob_path, file_type="image"):
    """Upload a file to GCS and track it."""
    client = get_gcs_client()
    if not client:
        return None
    
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(local_path)
        track_file(blob_path, file_type)
        return f"gs://{bucket_name}/{blob_path}"
    except Exception as e:
        print(f"Error uploading to {blob_path}: {e}")
        return None


def delete_from_gcs(bucket_name, blob_paths):
    """Delete files from GCS."""
    client = get_gcs_client()
    if not client:
        return []
    
    bucket = client.bucket(bucket_name)
    deleted = []
    
    for blob_path in blob_paths:
        try:
            path = blob_path['path'] if isinstance(blob_path, dict) else blob_path
            blob = bucket.blob(path)
            blob.delete()
            deleted.append(path)
        except Exception as e:
            print(f"Error deleting {blob_path}: {e}")
    
    return deleted


def delete_old_version_folders():
    """Delete output folders from previous versions."""
    if MODE == "KAGGLE":
        for item in os.listdir(KAGGLE_OUTPUT_PATH):
            item_path = os.path.join(KAGGLE_OUTPUT_PATH, item)
            if os.path.isdir(item_path) and '_color_split' in item and VERSION not in item:
                import shutil
                shutil.rmtree(item_path)
                print(f"Deleted old version folder: {item}")
    else:
        client = get_gcs_client()
        if not client:
            return
        
        bucket = client.bucket(GCS_BUCKET)
        for version_num in range(1, 20):
            if f"v{version_num}" == VERSION:
                continue
            old_prefix = f"v{version_num}_color_split/"
            blobs = list(bucket.list_blobs(prefix=old_prefix, max_results=100))
            if blobs:
                print(f"Deleting {len(blobs)} files from {old_prefix}...")
                for blob in blobs:
                    blob.delete()

# ============================================================================
#                   COLOR DETECTION (STEP 1: Monotone Check)
# ============================================================================

def detect_color_composition(image_bgr):
    """
    STEP 1: Detect if image has both red and black or is monotone.
    
    Returns dict with:
    - has_red: bool
    - has_black: bool  
    - is_monotone: bool
    - red_percent: float
    - black_percent: float
    - dominant_colors: list
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    total_pixels = image_bgr.shape[0] * image_bgr.shape[1]
    
    # Detect RED pixels (grid)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask_red1, mask_red2)
    
    # Also detect pink (lighter red grid)
    lower_pink = np.array([0, 20, 150])
    upper_pink = np.array([20, 100, 255])
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    
    red_total_mask = cv2.bitwise_or(red_mask, pink_mask)
    red_pixels = np.sum(red_total_mask > 0)
    red_percent = (red_pixels / total_pixels) * 100
    
    # Detect BLACK pixels (ECG traces)
    black_mask = gray < 80  # Dark pixels
    # Exclude red pixels from black count
    black_only_mask = black_mask & (red_total_mask == 0)
    black_pixels = np.sum(black_only_mask)
    black_percent = (black_pixels / total_pixels) * 100
    
    # Detect WHITE/PAPER pixels
    white_mask = gray > 200
    white_pixels = np.sum(white_mask)
    white_percent = (white_pixels / total_pixels) * 100
    
    # Determine color presence
    has_red = red_percent >= RED_THRESHOLD_PERCENT
    has_black = black_percent >= BLACK_THRESHOLD_PERCENT
    is_monotone = not (has_red and has_black)
    
    # Determine dominant colors
    dominant_colors = []
    if has_red:
        dominant_colors.append("red/pink")
    if has_black:
        dominant_colors.append("black")
    if white_percent > 50:
        dominant_colors.append("white (paper)")
    
    return {
        'has_red': has_red,
        'has_black': has_black,
        'is_monotone': is_monotone,
        'red_pixels': int(red_pixels),
        'red_percent': round(red_percent, 2),
        'black_pixels': int(black_pixels),
        'black_percent': round(black_percent, 2),
        'white_pixels': int(white_pixels),
        'white_percent': round(white_percent, 2),
        'dominant_colors': dominant_colors,
        'color_verdict': "COLOR (red+black)" if not is_monotone else "MONOTONE"
    }

# ============================================================================
#                   GRID CALIBRATION DETECTION
# ============================================================================

def detect_grid_spacing(image_bgr):
    """
    Detect grid line spacing to validate calibration assumptions.
    
    Returns dict with:
    - detected_small_square_px: estimated pixels per small square
    - detected_large_square_px: estimated pixels per large square
    - estimated_dpi: based on 1mm = detected pixels
    - confidence: how confident we are in the detection
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # Detect red grid lines using color
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 30, 30])
    upper_red1 = np.array([15, 255, 255])
    lower_red2 = np.array([165, 30, 30])
    upper_red2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    grid_mask = cv2.bitwise_or(mask1, mask2)
    
    # Find horizontal line spacing using projection
    h_projection = np.sum(grid_mask, axis=1)  # Sum along rows
    v_projection = np.sum(grid_mask, axis=0)  # Sum along columns
    
    # Find peaks in projections (grid lines)
    def find_spacing(projection, min_distance=5):
        # Threshold to find significant lines
        threshold = np.mean(projection) + np.std(projection)
        peaks = []
        for i in range(1, len(projection) - 1):
            if projection[i] > threshold:
                if projection[i] > projection[i-1] and projection[i] > projection[i+1]:
                    peaks.append(i)
        
        # Calculate spacing between peaks
        if len(peaks) < 2:
            return None, []
        
        spacings = []
        for i in range(1, len(peaks)):
            spacing = peaks[i] - peaks[i-1]
            if spacing >= min_distance:
                spacings.append(spacing)
        
        if not spacings:
            return None, peaks
        
        # Find most common spacing (small squares)
        from collections import Counter
        spacing_counts = Counter([round(s, -1) for s in spacings])  # Round to nearest 10
        if spacing_counts:
            most_common = spacing_counts.most_common(1)[0][0]
            return most_common, peaks
        
        return np.median(spacings), peaks
    
    h_spacing, h_peaks = find_spacing(h_projection)
    v_spacing, v_peaks = find_spacing(v_projection)
    
    # Average the horizontal and vertical spacings
    spacings = [s for s in [h_spacing, v_spacing] if s is not None]
    
    if spacings:
        avg_small_square_px = np.mean(spacings)
        # Large squares are 5 small squares
        avg_large_square_px = avg_small_square_px * 5
        
        # Estimate DPI: 1mm should equal avg_small_square_px
        # DPI = pixels per inch, and 1 inch = 25.4mm
        estimated_dpi = avg_small_square_px * 25.4
        
        confidence = "HIGH" if len(spacings) == 2 and abs(h_spacing - v_spacing) < 5 else "MEDIUM"
    else:
        avg_small_square_px = None
        avg_large_square_px = None
        estimated_dpi = None
        confidence = "LOW"
    
    return {
        'detected_small_square_px': round(avg_small_square_px, 1) if avg_small_square_px else None,
        'detected_large_square_px': round(avg_large_square_px, 1) if avg_large_square_px else None,
        'estimated_dpi': round(estimated_dpi, 0) if estimated_dpi else None,
        'horizontal_spacing_px': round(h_spacing, 1) if h_spacing else None,
        'vertical_spacing_px': round(v_spacing, 1) if v_spacing else None,
        'h_grid_lines_detected': len(h_peaks),
        'v_grid_lines_detected': len(v_peaks),
        'confidence': confidence,
        'grid_detected': avg_small_square_px is not None
    }


def validate_calibration(grid_info, image_shape):
    """
    Validate detected grid against ECG assumptions.
    
    Returns dict with validation results and warnings.
    """
    warnings = []
    validations = []
    
    height, width = image_shape[:2]
    
    if grid_info['detected_small_square_px']:
        px = grid_info['detected_small_square_px']
        dpi = grid_info['estimated_dpi']
        
        # Check DPI is in expected range
        min_dpi, max_dpi = ECG_ASSUMPTIONS['expected_dpi_range']
        if dpi and min_dpi <= dpi <= max_dpi:
            validations.append(f"DPI ({dpi:.0f}) is within expected range ({min_dpi}-{max_dpi})")
        elif dpi:
            warnings.append(f"DPI ({dpi:.0f}) is outside expected range ({min_dpi}-{max_dpi})")
        
        # Calculate voltage scale based on detected grid
        # At standard: 10mm = 1mV, so 10 small squares = 1mV
        mv_per_pixel = ECG_ASSUMPTIONS['mv_per_10mm'] / (px * 10)
        
        # Calculate time scale
        # At standard: 25mm/s, so 1mm = 40ms
        ms_per_pixel = ECG_ASSUMPTIONS['ms_per_small_square'] / px
        
        validations.append(f"Calculated: {mv_per_pixel*1000:.3f} uV/pixel")
        validations.append(f"Calculated: {ms_per_pixel:.3f} ms/pixel")
        
    else:
        warnings.append("Could not detect grid spacing - manual calibration may be needed")
    
    return {
        'validations': validations,
        'warnings': warnings,
        'calibration_valid': len(warnings) == 0
    }

# ============================================================================
#                   ANALYSIS MARKDOWN GENERATOR
# ============================================================================

def generate_analysis_md(filename, color_info, grid_info, calibration_info, processing_results):
    """
    Generate a markdown analysis file for the image.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    base_name = os.path.splitext(filename)[0]
    
    md_content = f"""# ECG Image Analysis Report

**File:** `{filename}`  
**Generated:** {timestamp}  
**Version:** {VERSION}  
**Mode:** {MODE}

---

## 1. Color Composition Analysis

| Metric | Value |
|--------|-------|
| **Color Verdict** | {color_info['color_verdict']} |
| **Has Red (Grid)** | {'Yes' if color_info['has_red'] else 'No'} |
| **Has Black (ECG)** | {'Yes' if color_info['has_black'] else 'No'} |
| **Is Monotone** | {'Yes' if color_info['is_monotone'] else 'No'} |

### Pixel Breakdown

| Color | Pixels | Percentage |
|-------|--------|------------|
| Red/Pink (Grid) | {color_info['red_pixels']:,} | {color_info['red_percent']:.2f}% |
| Black (ECG) | {color_info['black_pixels']:,} | {color_info['black_percent']:.2f}% |
| White (Paper) | {color_info['white_pixels']:,} | {color_info['white_percent']:.2f}% |

**Dominant Colors:** {', '.join(color_info['dominant_colors']) if color_info['dominant_colors'] else 'None detected'}

---

## 2. Grid Calibration Detection

| Metric | Detected Value |
|--------|----------------|
| **Small Square (px)** | {grid_info['detected_small_square_px'] or 'N/A'} |
| **Large Square (px)** | {grid_info['detected_large_square_px'] or 'N/A'} |
| **Estimated DPI** | {grid_info['estimated_dpi'] or 'N/A'} |
| **H Grid Lines** | {grid_info['h_grid_lines_detected']} |
| **V Grid Lines** | {grid_info['v_grid_lines_detected']} |
| **Detection Confidence** | {grid_info['confidence']} |

---

## 3. ECG Calibration Assumptions

### Standard ECG Paper Specifications (Assumed)

| Parameter | Standard Value | Notes |
|-----------|----------------|-------|
| **Small Square** | {ECG_ASSUMPTIONS['grid_small_square_mm']} mm | 1mm x 1mm |
| **Large Square** | {ECG_ASSUMPTIONS['grid_large_square_mm']} mm | 5mm x 5mm (5 small squares) |
| **Voltage Scale** | {ECG_ASSUMPTIONS['mv_per_10mm']} mV/10mm | 10 small squares = 1mV |
| **Per Small Square** | {ECG_ASSUMPTIONS['mv_per_small_square']} mV | Vertical |
| **Paper Speed** | {ECG_ASSUMPTIONS['paper_speed_mm_per_sec']} mm/s | Horizontal |
| **Time per Square** | {ECG_ASSUMPTIONS['ms_per_small_square']} ms | Per 1mm |
| **Calibration Pulse** | {ECG_ASSUMPTIONS['calibration_pulse_mv']} mV | Reference marker |

### Validation Results

"""
    
    if calibration_info['validations']:
        md_content += "**Passed:**\n"
        for v in calibration_info['validations']:
            md_content += f"- {v}\n"
    
    if calibration_info['warnings']:
        md_content += "\n**Warnings:**\n"
        for w in calibration_info['warnings']:
            md_content += f"- {w}\n"
    
    md_content += f"""
---

## 4. Processing Results

"""
    
    if color_info['is_monotone']:
        md_content += """
> **MONOTONE IMAGE DETECTED**
> 
> This image does not contain both red grid and black ECG traces.
> Color separation was not performed.

"""
    else:
        md_content += "### Method Comparison\n\n"
        md_content += "| Method | BLACK Score | RED Score | Notes |\n"
        md_content += "|--------|-------------|-----------|-------|\n"
        
        for method, data in processing_results.get('methods', {}).items():
            black_score = data.get('black_score', 'N/A')
            red_score = data.get('red_score', 'N/A')
            md_content += f"| {method} | {black_score:,} | {red_score} | |\n"
        
        if 'keeper_black' in processing_results:
            kb = processing_results['keeper_black']
            md_content += f"\n**Best BLACK:** {kb['method']} (score: {kb['score']:,})\n"
        
        if 'keeper_red' in processing_results:
            kr = processing_results['keeper_red']
            md_content += f"**Best RED:** {kr['method']} (score: {kr['score']})\n"
    
    md_content += f"""
---

## 5. Output Files

| File Type | Filename |
|-----------|----------|
| Original | `{base_name}--original.png` |
"""
    
    for f in processing_results.get('local_files', []):
        fname = os.path.basename(f)
        if '--sk-' in fname:
            md_content += f"| **KEEPER** | `{fname}` |\n"
        elif '--s-' in fname:
            md_content += f"| Processed | `{fname}` |\n"
    
    md_content += f"""
---

## 6. Interpretation Guide

### Voltage (Y-axis)
- 1 small square (1mm) = **{ECG_ASSUMPTIONS['mv_per_small_square']} mV**
- 1 large square (5mm) = **{ECG_ASSUMPTIONS['mv_per_large_square']} mV**
- Full scale typically ±5 mV

### Time (X-axis)
- 1 small square (1mm) = **{ECG_ASSUMPTIONS['ms_per_small_square']} ms**
- 1 large square (5mm) = **{ECG_ASSUMPTIONS['ms_per_large_square']} ms**
- Typical ECG duration: 2.5-10 seconds

### Quality Scores
- **BLACK Score:** Total black pixels (HIGHER = more ECG data captured)
- **RED Score:** % black contamination × 1000 (LOWER = cleaner grid)

---

*Report generated by ECG Color Processor {VERSION}*
"""
    
    return md_content

# ============================================================================
#                         IMAGE PROCESSING FUNCTIONS
# ============================================================================

def detect_text_regions(image_bgr):
    """Detect text regions in ECG image."""
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
    
    img_h, img_w = gray.shape
    
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        aspect_ratio = w / max(h, 1)
        is_text = False
        
        if area < 5000 and area > 50:
            if aspect_ratio > 2 or aspect_ratio < 0.5:
                is_text = True
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
    """RED score: % black pixels × 1000 (LOWER = better)"""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    black_pixels = np.sum(gray < 50)
    total_pixels = gray.size
    return int((black_pixels / total_pixels) * 100 * 1000)


def calculate_black_quality_score(image_bgr):
    """BLACK score: total black pixels (HIGHER = better)"""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return int(np.sum(gray < 50))


# ----- OPENCV METHOD -----
def isolate_ecg_opencv(image_bgr, remove_text=True):
    """Remove red grid using OpenCV HSV, keep black ECG traces."""
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
    
    if remove_text and REMOVE_TEXT:
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


# ----- PILLOW METHOD -----
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
    
    if remove_text and REMOVE_TEXT:
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


# ============================================================================
#                         FILENAME GENERATION
# ============================================================================

def generate_output_filename(original_filename, method, color_type, score, is_keeper=False):
    """Generate output filename."""
    base = os.path.splitext(os.path.basename(original_filename))[0]
    prefix = "--sk-" if is_keeper else "--s-"
    return f"{base}{prefix}{VERSION}-{method}-{color_type}-{score}.png"


def generate_original_filename(original_filename):
    """Generate filename for original image copy."""
    base = os.path.splitext(os.path.basename(original_filename))[0]
    return f"{base}--original.png"


def generate_analysis_filename(original_filename):
    """Generate filename for analysis markdown."""
    base = os.path.splitext(os.path.basename(original_filename))[0]
    return f"{base}--analysis-{VERSION}.md"


# ============================================================================
#                         SINGLE IMAGE PROCESSOR
# ============================================================================

def process_single_image(image_path_or_gcs, output_dir=None):
    """Process a single image with full analysis."""
    filename = os.path.basename(image_path_or_gcs)
    base_name = os.path.splitext(filename)[0]
    
    if output_dir is None:
        output_dir = LOCAL_TEMP
    
    # Load image
    if MODE in ["CLOUD", "GROUP"] and image_path_or_gcs.startswith(GCS_SOURCE_FOLDER):
        local_path = os.path.join(LOCAL_TEMP, filename)
        if not download_from_gcs(GCS_BUCKET, image_path_or_gcs, local_path):
            return None
        image = cv2.imread(local_path)
    else:
        image = cv2.imread(image_path_or_gcs)
        local_path = image_path_or_gcs
    
    if image is None:
        print(f"  Error: Could not read image: {filename}")
        return None
    
    print(f"  Image size: {image.shape[1]}x{image.shape[0]}")
    
    # ===== STEP 1: COLOR COMPOSITION CHECK =====
    print(f"  Step 1: Checking color composition...")
    color_info = detect_color_composition(image)
    print(f"    Verdict: {color_info['color_verdict']}")
    print(f"    Red: {color_info['red_percent']:.1f}% | Black: {color_info['black_percent']:.1f}%")
    
    # ===== STEP 2: GRID CALIBRATION DETECTION =====
    print(f"  Step 2: Detecting grid calibration...")
    grid_info = detect_grid_spacing(image)
    print(f"    Small square: {grid_info['detected_small_square_px']} px")
    print(f"    Estimated DPI: {grid_info['estimated_dpi']}")
    print(f"    Confidence: {grid_info['confidence']}")
    
    # ===== STEP 3: VALIDATE CALIBRATION =====
    calibration_info = validate_calibration(grid_info, image.shape)
    if calibration_info['warnings']:
        for w in calibration_info['warnings']:
            print(f"    Warning: {w}")
    
    # Initialize results
    results = {
        'source': image_path_or_gcs,
        'filename': filename,
        'color_info': color_info,
        'grid_info': grid_info,
        'calibration_info': calibration_info,
        'methods': {},
        'black_scores': {},
        'red_scores': {},
        'uploaded_files': [],
        'local_files': []
    }
    
    # Save original for comparison
    if SAVE_ORIGINALS:
        original_filename = generate_original_filename(filename)
        original_local = os.path.join(output_dir, original_filename)
        cv2.imwrite(original_local, image)
        results['local_files'].append(original_local)
        
        if MODE in ["CLOUD", "GROUP"]:
            original_gcs = f"{GCS_OUTPUT_FOLDER}/{original_filename}"
            upload_to_gcs(original_local, GCS_BUCKET, original_gcs, "original")
            results['uploaded_files'].append(original_gcs)
    
    # ===== STEP 4: COLOR SEPARATION (if not monotone) =====
    if color_info['is_monotone']:
        print(f"  Step 4: SKIPPED - Image is monotone, no color separation needed")
    else:
        print(f"  Step 4: Processing color separation...")
        
        for method in METHODS:
            print(f"    Method: {method}")
            
            if method == 'opencv':
                ecg_func = isolate_ecg_opencv
                grid_func = isolate_grid_opencv
            elif method == 'pillow':
                ecg_func = isolate_ecg_pillow
                grid_func = isolate_grid_pillow
            else:
                continue
            
            # Process ECG (black)
            ecg_img, ecg_pixels = ecg_func(image)
            black_score = calculate_black_quality_score(ecg_img)
            results['black_scores'][method] = black_score
            
            # Process Grid (red)
            grid_img, grid_pixels = grid_func(image)
            red_score = calculate_red_quality_score(grid_img)
            results['red_scores'][method] = red_score
            
            print(f"      BLACK: {black_score:,} pixels | RED: {red_score} contamination")
            
            results['methods'][method] = {
                'ecg_pixels': ecg_pixels,
                'grid_pixels': grid_pixels,
                'black_score': black_score,
                'red_score': red_score,
                'ecg_img': ecg_img,
                'grid_img': grid_img
            }
            
            # Save BLACK image
            if ecg_pixels >= MIN_ECG_PIXELS:
                black_filename = generate_output_filename(filename, method, 'black', black_score)
                black_local = os.path.join(output_dir, black_filename)
                cv2.imwrite(black_local, ecg_img)
                results['local_files'].append(black_local)
                results['methods'][method]['black_path'] = black_local
                
                if MODE in ["CLOUD", "GROUP"]:
                    black_gcs = f"{GCS_OUTPUT_FOLDER}/{black_filename}"
                    upload_to_gcs(black_local, GCS_BUCKET, black_gcs, "processed")
                    results['uploaded_files'].append(black_gcs)
            
            # Save RED image
            if grid_pixels >= MIN_GRID_PIXELS:
                red_filename = generate_output_filename(filename, method, 'red', red_score)
                red_local = os.path.join(output_dir, red_filename)
                cv2.imwrite(red_local, grid_img)
                results['local_files'].append(red_local)
                results['methods'][method]['red_path'] = red_local
                
                if MODE in ["CLOUD", "GROUP"]:
                    red_gcs = f"{GCS_OUTPUT_FOLDER}/{red_filename}"
                    upload_to_gcs(red_local, GCS_BUCKET, red_gcs, "processed")
                    results['uploaded_files'].append(red_gcs)
        
        # Select KEEPERS
        if results['black_scores']:
            best_black_method = max(results['black_scores'], key=results['black_scores'].get)
            best_black_score = results['black_scores'][best_black_method]
            best_black_img = results['methods'][best_black_method]['ecg_img']
            
            keeper_black_filename = generate_output_filename(filename, best_black_method, 'black', best_black_score, is_keeper=True)
            keeper_black_local = os.path.join(output_dir, keeper_black_filename)
            cv2.imwrite(keeper_black_local, best_black_img)
            results['local_files'].append(keeper_black_local)
            results['keeper_black'] = {'method': best_black_method, 'score': best_black_score}
            print(f"    KEEPER BLACK: {best_black_method} (score: {best_black_score:,})")
            
            if MODE in ["CLOUD", "GROUP"]:
                keeper_black_gcs = f"{GCS_OUTPUT_FOLDER}/{keeper_black_filename}"
                upload_to_gcs(keeper_black_local, GCS_BUCKET, keeper_black_gcs, "keeper")
                results['uploaded_files'].append(keeper_black_gcs)
        
        if results['red_scores']:
            best_red_method = min(results['red_scores'], key=results['red_scores'].get)
            best_red_score = results['red_scores'][best_red_method]
            best_red_img = results['methods'][best_red_method]['grid_img']
            
            keeper_red_filename = generate_output_filename(filename, best_red_method, 'red', best_red_score, is_keeper=True)
            keeper_red_local = os.path.join(output_dir, keeper_red_filename)
            cv2.imwrite(keeper_red_local, best_red_img)
            results['local_files'].append(keeper_red_local)
            results['keeper_red'] = {'method': best_red_method, 'score': best_red_score}
            print(f"    KEEPER RED: {best_red_method} (score: {best_red_score})")
            
            if MODE in ["CLOUD", "GROUP"]:
                keeper_red_gcs = f"{GCS_OUTPUT_FOLDER}/{keeper_red_filename}"
                upload_to_gcs(keeper_red_local, GCS_BUCKET, keeper_red_gcs, "keeper")
                results['uploaded_files'].append(keeper_red_gcs)
    
    # ===== STEP 5: GENERATE ANALYSIS MD =====
    if GENERATE_ANALYSIS_MD:
        print(f"  Step 5: Generating analysis report...")
        md_content = generate_analysis_md(filename, color_info, grid_info, calibration_info, results)
        
        analysis_filename = generate_analysis_filename(filename)
        analysis_local = os.path.join(output_dir, analysis_filename)
        
        with open(analysis_local, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        results['local_files'].append(analysis_local)
        results['analysis_file'] = analysis_local
        
        if MODE in ["CLOUD", "GROUP"]:
            analysis_gcs = f"{GCS_OUTPUT_FOLDER}/{analysis_filename}"
            upload_to_gcs(analysis_local, GCS_BUCKET, analysis_gcs, "analysis")
            results['uploaded_files'].append(analysis_gcs)
            print(f"    Uploaded: {analysis_filename}")
    
    # Clean up image data
    for method in results['methods']:
        if 'ecg_img' in results['methods'][method]:
            del results['methods'][method]['ecg_img']
        if 'grid_img' in results['methods'][method]:
            del results['methods'][method]['grid_img']
    
    return results


# ============================================================================
#                         GROUP SELECTION LOGIC
# ============================================================================

def get_selected_groups():
    """Get the list of group prefixes to process."""
    if not IMAGE_GROUP_PREFIXES:
        print("Warning: IMAGE_GROUP_PREFIXES is empty.")
        return []
    
    if GROUP_SELECTION_MODE == "RANGE":
        start = max(0, GROUP_RANGE_START)
        end = min(len(IMAGE_GROUP_PREFIXES), GROUP_RANGE_END)
        selected = IMAGE_GROUP_PREFIXES[start:end]
        print(f"Selected groups {start} to {end-1}: {selected}")
        return selected
    
    elif GROUP_SELECTION_MODE == "RANDOM":
        count = min(GROUP_RANDOM_COUNT, len(IMAGE_GROUP_PREFIXES))
        selected = random.sample(IMAGE_GROUP_PREFIXES, count)
        print(f"Randomly selected {count} groups: {selected}")
        return selected
    
    elif GROUP_SELECTION_MODE == "LIST":
        selected = [IMAGE_GROUP_PREFIXES[i] for i in GROUP_LIST if i < len(IMAGE_GROUP_PREFIXES)]
        print(f"Selected groups from list: {selected}")
        return selected
    
    return IMAGE_GROUP_PREFIXES


# ============================================================================
#                         BATCH PROCESSING
# ============================================================================

def find_kaggle_images(limit=None):
    """Find images in Kaggle input path."""
    images = []
    train_path = os.path.join(KAGGLE_INPUT_PATH, "train")
    if os.path.exists(train_path):
        for root, dirs, files in os.walk(train_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    if '--s-' not in file and '--sk-' not in file:
                        images.append(os.path.join(root, file))
                        if limit and len(images) >= limit:
                            return images
    return images


def find_local_images(folder, limit=None):
    """Find images in a local folder."""
    images = []
    if not os.path.exists(folder):
        print(f"Warning: Local folder does not exist: {folder}")
        print(f"Creating folder and adding placeholder message...")
        os.makedirs(folder, exist_ok=True)
        readme_path = os.path.join(folder, "README.txt")
        with open(readme_path, 'w') as f:
            f.write("Place ECG images (.png, .jpg) in this folder for processing.\n")
        return []
    
    for file in os.listdir(folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Skip already processed
            if '--s-' not in file and '--sk-' not in file and '--original' not in file:
                images.append(os.path.join(folder, file))
                if limit and len(images) >= limit:
                    break
    
    return images


def process_batch_local():
    """Process images in LOCAL mode (no GCS needed)."""
    print("\n" + "=" * 60)
    print("LOCAL MODE - Processing Local Files")
    print("=" * 60)
    print(f"Input folder: {LOCAL_INPUT_FOLDER}")
    print(f"Output folder: {LOCAL_OUTPUT_FOLDER}")
    
    # Create output folder
    os.makedirs(LOCAL_OUTPUT_FOLDER, exist_ok=True)
    
    # Find images
    images = find_local_images(LOCAL_INPUT_FOLDER, limit=TEST_LIMIT)
    print(f"Found {len(images)} images to process")
    
    if not images:
        print("\nNo images found!")
        print(f"Please add ECG images to: {LOCAL_INPUT_FOLDER}")
        return []
    
    all_results = []
    for i, img_path in enumerate(images):
        print(f"\n[{i+1}/{len(images)}] {os.path.basename(img_path)}")
        result = process_single_image(img_path, LOCAL_OUTPUT_FOLDER)
        if result:
            all_results.append(result)
    
    return all_results


def process_batch_kaggle():
    """Process images in Kaggle mode."""
    print("\n" + "=" * 60)
    print("KAGGLE MODE - Processing Competition Dataset")
    print("=" * 60)
    
    output_dir = os.path.join(KAGGLE_OUTPUT_PATH, f"{VERSION}_color_split")
    os.makedirs(output_dir, exist_ok=True)
    
    images = find_kaggle_images(limit=TEST_LIMIT)
    print(f"Found {len(images)} images to process")
    
    if not images:
        return []
    
    all_results = []
    for i, img_path in enumerate(images):
        print(f"\n[{i+1}/{len(images)}] {os.path.basename(img_path)}")
        result = process_single_image(img_path, output_dir)
        if result:
            all_results.append(result)
    
    return all_results


def process_batch_cloud():
    """Process all images from GCS."""
    print("\n" + "=" * 60)
    print("CLOUD MODE - Processing All Images from GCS")
    print("=" * 60)
    
    if DELETE_OLD_VERSIONS:
        delete_old_version_folders()
    
    images = list_gcs_images(GCS_BUCKET, GCS_SOURCE_FOLDER, limit=TEST_LIMIT)
    print(f"Found {len(images)} images to process")
    
    if not images:
        return []
    
    all_results = []
    for i, gcs_path in enumerate(images):
        print(f"\n[{i+1}/{len(images)}] {os.path.basename(gcs_path)}")
        result = process_single_image(gcs_path)
        if result:
            all_results.append(result)
    
    return all_results


def process_batch_group():
    """Process specific image groups."""
    print("\n" + "=" * 60)
    print("GROUP MODE - Processing Selected Image Groups")
    print("=" * 60)
    
    selected_prefixes = get_selected_groups()
    if not selected_prefixes:
        return []
    
    if DELETE_OLD_VERSIONS:
        delete_old_version_folders()
    
    images = list_gcs_images(GCS_BUCKET, GCS_SOURCE_FOLDER, 
                             prefix_filter=set(selected_prefixes), 
                             limit=TEST_LIMIT)
    print(f"Found {len(images)} images in selected groups")
    
    if not images:
        return []
    
    all_results = []
    for i, gcs_path in enumerate(images):
        print(f"\n[{i+1}/{len(images)}] {os.path.basename(gcs_path)}")
        result = process_single_image(gcs_path)
        if result:
            all_results.append(result)
    
    return all_results


# ============================================================================
#                         RESULTS SUMMARY
# ============================================================================

def print_summary(all_results):
    """Print processing summary."""
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE - SUMMARY")
    print("=" * 60)
    
    total_images = len(all_results)
    
    # Count by type
    monotone_count = sum(1 for r in all_results if r['color_info']['is_monotone'])
    color_count = total_images - monotone_count
    
    # File counts by type
    file_counts = defaultdict(int)
    for f in CREATED_FILES:
        file_counts[f['type']] += 1
    
    print(f"Images processed: {total_images}")
    print(f"  - Color (red+black): {color_count}")
    print(f"  - Monotone: {monotone_count}")
    print(f"\nFiles created by type:")
    for ftype, count in sorted(file_counts.items()):
        print(f"  - {ftype}: {count}")
    print(f"  - TOTAL: {len(CREATED_FILES)}")
    
    # Calibration summary
    high_conf = sum(1 for r in all_results if r['grid_info']['confidence'] == 'HIGH')
    med_conf = sum(1 for r in all_results if r['grid_info']['confidence'] == 'MEDIUM')
    low_conf = sum(1 for r in all_results if r['grid_info']['confidence'] == 'LOW')
    
    print(f"\nGrid detection confidence:")
    print(f"  - HIGH: {high_conf}")
    print(f"  - MEDIUM: {med_conf}")
    print(f"  - LOW: {low_conf}")
    
    return {
        'total_images': total_images,
        'color_images': color_count,
        'monotone_images': monotone_count,
        'files_by_type': dict(file_counts),
        'total_files': len(CREATED_FILES)
    }


def save_session_manifest():
    """Save manifest of all created files for this session."""
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'version': VERSION,
        'mode': MODE,
        'created_files': CREATED_FILES
    }
    
    manifest_path = os.path.join(LOCAL_TEMP, f'session_manifest_{VERSION}.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\nSession manifest saved: {manifest_path}")
    
    if MODE in ["CLOUD", "GROUP"]:
        manifest_gcs = f"{GCS_OUTPUT_FOLDER}/session_manifest_{VERSION}.json"
        upload_to_gcs(manifest_path, GCS_BUCKET, manifest_gcs, "manifest")
        print(f"Uploaded to: gs://{GCS_BUCKET}/{manifest_gcs}")
    
    return manifest_path


# ============================================================================
#                         CLEANUP FUNCTIONS
# ============================================================================

def delete_all_created():
    """Delete all files created in this session."""
    if MODE in ["CLOUD", "GROUP"] and CREATED_FILES:
        paths = [f['path'] for f in CREATED_FILES]
        print(f"\nDeleting {len(paths)} created files...")
        deleted = delete_from_gcs(GCS_BUCKET, paths)
        print(f"Deleted {len(deleted)} files")


def delete_by_type(file_type):
    """Delete files of a specific type."""
    files = [f for f in CREATED_FILES if f['type'] == file_type]
    if files:
        paths = [f['path'] for f in files]
        print(f"\nDeleting {len(paths)} {file_type} files...")
        deleted = delete_from_gcs(GCS_BUCKET, paths)
        print(f"Deleted {len(deleted)} files")


def delete_local_files(del_type):
    """Delete local files from output folder by type."""
    if not os.path.exists(LOCAL_OUTPUT_FOLDER):
        print("Output folder does not exist.")
        return
    
    files_to_delete = []
    
    for f in os.listdir(LOCAL_OUTPUT_FOLDER):
        if del_type == 'a' and (f'--{VERSION}' in f or f'--analysis-{VERSION}' in f):
            files_to_delete.append(f)
        elif del_type == 'p' and '--s-' in f and '--sk-' not in f:
            files_to_delete.append(f)
        elif del_type == 'k' and '--sk-' in f:
            files_to_delete.append(f)
        elif del_type == 'm' and f.endswith('.md'):
            files_to_delete.append(f)
        elif del_type == 'o' and '--original' in f:
            files_to_delete.append(f)
    
    if not files_to_delete:
        print("No matching files found.")
        return
    
    print(f"\nFound {len(files_to_delete)} files to delete:")
    for f in files_to_delete[:10]:
        print(f"  {f}")
    if len(files_to_delete) > 10:
        print(f"  ... and {len(files_to_delete) - 10} more")
    
    confirm = input("\nDelete these files? (y/n): ").strip().lower()
    if confirm == 'y':
        for f in files_to_delete:
            try:
                os.remove(os.path.join(LOCAL_OUTPUT_FOLDER, f))
            except Exception as e:
                print(f"Error deleting {f}: {e}")
        print(f"Deleted {len(files_to_delete)} files.")
    else:
        print("Cancelled.")


def process_gcs_all_images(limit=None):
    """Process ALL images from GCS without group filtering."""
    print("\n" + "=" * 60)
    print("GCS → LOCAL: Process ALL Images")
    print("=" * 60)
    print(f"GCS Bucket: {GCS_BUCKET}")
    print(f"Local Output: {LOCAL_OUTPUT_FOLDER}")
    print(f"Limit: {limit if limit else 'None (all images)'}")
    
    # List ALL images from GCS (no prefix filter)
    print("\nConnecting to GCS and listing images...")
    images = list_all_gcs_images_no_filter(GCS_BUCKET, limit=limit)
    print(f"Found {len(images)} images")
    
    if not images:
        print("No images found!")
        return []
    
    # Create output folder
    os.makedirs(LOCAL_OUTPUT_FOLDER, exist_ok=True)
    
    import time
    all_results = []
    total_start = time.time()
    
    for i, gcs_path in enumerate(images):
        filename = os.path.basename(gcs_path)
        
        # Calculate ETA
        if i > 0:
            elapsed = time.time() - total_start
            avg_per_image = elapsed / i
            remaining = (len(images) - i) * avg_per_image
            eta_str = f" | ETA: {remaining/60:.1f} min" if remaining > 60 else f" | ETA: {remaining:.0f}s"
        else:
            eta_str = ""
        
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(images)}] {filename}{eta_str}")
        print(f"{'='*60}")
        
        # Download from GCS to temp
        local_temp_path = os.path.join(LOCAL_TEMP, filename)
        if not download_from_gcs(GCS_BUCKET, gcs_path, local_temp_path):
            continue
        
        # Process and save to LOCAL_OUTPUT_FOLDER
        result = process_single_image_local_only(local_temp_path, LOCAL_OUTPUT_FOLDER)
        if result:
            all_results.append(result)
        
        # Clean up temp file
        try:
            os.remove(local_temp_path)
        except:
            pass
    
    # Print summary
    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {len(all_results)}/{len(images)} images in {total_time/60:.1f} minutes")
    print(f"{'='*60}")
    
    if all_results:
        print_summary(all_results)
        save_session_manifest()
    
    return all_results


def process_gcs_to_local():
    """Download from GCS, process, save locally only (no upload back)."""
    print("\n" + "=" * 60)
    print("GCS → LOCAL: Download, Process, Save Locally")
    print("=" * 60)
    print(f"GCS Bucket: {GCS_BUCKET}")
    print(f"GCS Source: {GCS_SOURCE_FOLDER}")
    print(f"Local Output: {LOCAL_OUTPUT_FOLDER}")
    
    # Get selected groups
    selected_prefixes = get_selected_groups()
    if not selected_prefixes:
        print("No groups selected!")
        return []
    
    # List images from GCS
    print("\nConnecting to GCS...")
    images = list_gcs_images(GCS_BUCKET, GCS_SOURCE_FOLDER, 
                             prefix_filter=set(selected_prefixes), 
                             limit=TEST_LIMIT)
    print(f"Found {len(images)} images in selected groups")
    
    if not images:
        print("No images found!")
        return []
    
    # Create output folder
    os.makedirs(LOCAL_OUTPUT_FOLDER, exist_ok=True)
    
    import time
    all_results = []
    total_start = time.time()
    
    for i, gcs_path in enumerate(images):
        filename = os.path.basename(gcs_path)
        
        # Calculate ETA
        if i > 0:
            elapsed = time.time() - total_start
            avg_per_image = elapsed / i
            remaining = (len(images) - i) * avg_per_image
            eta_str = f" | ETA: {remaining/60:.1f} min" if remaining > 60 else f" | ETA: {remaining:.0f}s"
        else:
            eta_str = ""
        
        print(f"\n{'='*60}")
        print(f"[{i+1}/{len(images)}] {filename}{eta_str}")
        print(f"{'='*60}")
        
        # Download from GCS to temp
        local_temp_path = os.path.join(LOCAL_TEMP, filename)
        if not download_from_gcs(GCS_BUCKET, gcs_path, local_temp_path):
            continue
        
        # Process and save to LOCAL_OUTPUT_FOLDER
        result = process_single_image_local_only(local_temp_path, LOCAL_OUTPUT_FOLDER)
        if result:
            all_results.append(result)
        
        # Clean up temp file
        try:
            os.remove(local_temp_path)
        except:
            pass
    
    # Print summary
    total_time = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {len(all_results)}/{len(images)} images in {total_time/60:.1f} minutes")
    print(f"{'='*60}")
    
    if all_results:
        print_summary(all_results)
        save_session_manifest()
    
    return all_results


def process_single_image_local_only(image_path, output_dir):
    """Process image and save ONLY to local folder (no GCS upload)."""
    import time
    start_time = time.time()
    
    filename = os.path.basename(image_path)
    base_name = os.path.splitext(filename)[0]
    
    print(f"  Loading image...", end=" ", flush=True)
    image = cv2.imread(image_path)
    if image is None:
        print(f"FAILED")
        return None
    print(f"OK ({image.shape[1]}x{image.shape[0]})")
    
    # Step 1: Color check
    print(f"  [1/5] Color analysis...", end=" ", flush=True)
    t0 = time.time()
    color_info = detect_color_composition(image)
    print(f"{color_info['color_verdict']} ({time.time()-t0:.1f}s)")
    
    # Step 2: Grid detection
    print(f"  [2/5] Grid detection...", end=" ", flush=True)
    t0 = time.time()
    grid_info = detect_grid_spacing(image)
    print(f"{grid_info['confidence']} ({time.time()-t0:.1f}s)")
    
    # Step 3: Calibration
    print(f"  [3/5] Calibration...", end=" ", flush=True)
    t0 = time.time()
    calibration_info = validate_calibration(grid_info, image.shape)
    print(f"OK ({time.time()-t0:.1f}s)")
    
    results = {
        'filename': filename,
        'color_info': color_info,
        'grid_info': grid_info,
        'calibration_info': calibration_info,
        'methods': {},
        'black_scores': {},
        'red_scores': {},
        'local_files': []
    }
    
    # Save original
    if SAVE_ORIGINALS:
        print(f"  [4/5] Saving original...", end=" ", flush=True)
        t0 = time.time()
        original_filename = generate_original_filename(filename)
        original_path = os.path.join(output_dir, original_filename)
        cv2.imwrite(original_path, image)
        results['local_files'].append(original_path)
        track_file(original_path, "original")
        print(f"OK ({time.time()-t0:.1f}s)")
    
    # Process if not monotone
    if not color_info['is_monotone']:
        print(f"  [5/5] Color separation ({len(METHODS)} methods)...")
        
        for i, method in enumerate(METHODS):
            print(f"        [{i+1}/{len(METHODS)}] {method}...", end=" ", flush=True)
            t0 = time.time()
            
            if method == 'opencv':
                ecg_img, ecg_pixels = isolate_ecg_opencv(image)
                grid_img, grid_pixels = isolate_grid_opencv(image)
            elif method == 'pillow':
                ecg_img, ecg_pixels = isolate_ecg_pillow(image)
                grid_img, grid_pixels = isolate_grid_pillow(image)
            else:
                print("SKIPPED")
                continue
            
            black_score = calculate_black_quality_score(ecg_img)
            red_score = calculate_red_quality_score(grid_img)
            
            results['black_scores'][method] = black_score
            results['red_scores'][method] = red_score
            results['methods'][method] = {
                'black_score': black_score,
                'red_score': red_score,
                'ecg_img': ecg_img,
                'grid_img': grid_img
            }
            
            print(f"B:{black_score:,} R:{red_score} ({time.time()-t0:.1f}s)")
            
            # Save black
            if ecg_pixels >= MIN_ECG_PIXELS:
                print(f"              Saving black...", end=" ", flush=True)
                black_filename = generate_output_filename(filename, method, 'black', black_score)
                black_path = os.path.join(output_dir, black_filename)
                cv2.imwrite(black_path, ecg_img)
                results['local_files'].append(black_path)
                track_file(black_path, "processed")
                print("OK")
            
            # Save red
            if grid_pixels >= MIN_GRID_PIXELS:
                print(f"              Saving red...", end=" ", flush=True)
                red_filename = generate_output_filename(filename, method, 'red', red_score)
                red_path = os.path.join(output_dir, red_filename)
                cv2.imwrite(red_path, grid_img)
                results['local_files'].append(red_path)
                track_file(red_path, "processed")
                print("OK")
        
        # Save keepers
        if results['black_scores']:
            print(f"        Saving KEEPER (best black)...", end=" ", flush=True)
            best_black = max(results['black_scores'], key=results['black_scores'].get)
            keeper_black_filename = generate_output_filename(filename, best_black, 'black', 
                                                             results['black_scores'][best_black], is_keeper=True)
            keeper_path = os.path.join(output_dir, keeper_black_filename)
            cv2.imwrite(keeper_path, results['methods'][best_black]['ecg_img'])
            results['local_files'].append(keeper_path)
            results['keeper_black'] = {'method': best_black, 'score': results['black_scores'][best_black]}
            track_file(keeper_path, "keeper")
            print(f"{best_black} (score: {results['black_scores'][best_black]:,})")
        
        if results['red_scores']:
            print(f"        Saving KEEPER (best red)...", end=" ", flush=True)
            best_red = min(results['red_scores'], key=results['red_scores'].get)
            keeper_red_filename = generate_output_filename(filename, best_red, 'red',
                                                           results['red_scores'][best_red], is_keeper=True)
            keeper_path = os.path.join(output_dir, keeper_red_filename)
            cv2.imwrite(keeper_path, results['methods'][best_red]['grid_img'])
            results['local_files'].append(keeper_path)
            results['keeper_red'] = {'method': best_red, 'score': results['red_scores'][best_red]}
            track_file(keeper_path, "keeper")
            print(f"{best_red} (score: {results['red_scores'][best_red]})")
    else:
        print(f"  [5/5] Color separation SKIPPED - Image is monotone")
    
    # Generate analysis MD
    if GENERATE_ANALYSIS_MD:
        print(f"  Generating analysis report...", end=" ", flush=True)
        t0 = time.time()
        md_content = generate_analysis_md(filename, color_info, grid_info, calibration_info, results)
        analysis_filename = generate_analysis_filename(filename)
        analysis_path = os.path.join(output_dir, analysis_filename)
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        results['local_files'].append(analysis_path)
        track_file(analysis_path, "analysis")
        print(f"OK ({time.time()-t0:.1f}s)")
    
    # Clean up image data
    for method in results['methods']:
        if 'ecg_img' in results['methods'][method]:
            del results['methods'][method]['ecg_img']
        if 'grid_img' in results['methods'][method]:
            del results['methods'][method]['grid_img']
    
    total_time = time.time() - start_time
    files_created = len(results['local_files'])
    print(f"  DONE: {files_created} files created in {total_time:.1f}s")
    
    return results


# ============================================================================
#                         MAIN ENTRY POINT
# ============================================================================

def main():
    """Main processing function."""
    print("\n" + "=" * 70)
    print("   ECG COLOR PROCESSOR - Version " + VERSION)
    print("=" * 70)
    print(f"Mode: {MODE}")
    print(f"Test limit: {TEST_LIMIT if TEST_LIMIT else 'None (all images)'}")
    print("\nECG Calibration Assumptions:")
    print(f"  Grid: {ECG_ASSUMPTIONS['grid_small_square_mm']}mm squares")
    print(f"  Voltage: {ECG_ASSUMPTIONS['mv_per_10mm']}mV per 10mm")
    print(f"  Speed: {ECG_ASSUMPTIONS['paper_speed_mm_per_sec']}mm/s")
    print("=" * 70)
    
    if MODE == "KAGGLE":
        all_results = process_batch_kaggle()
    elif MODE == "CLOUD":
        all_results = process_batch_cloud()
    elif MODE == "GROUP":
        all_results = process_batch_group()
    elif MODE == "LOCAL":
        all_results = process_batch_local()
    else:
        print(f"Unknown mode: {MODE}")
        return
    
    if not all_results:
        print("No images were processed!")
        return
    
    summary = print_summary(all_results)
    save_session_manifest()
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    
    return all_results


# ============================================================================
#                         INTERACTIVE CLI
# ============================================================================

def select_groups_interactive():
    """Interactive group selection at startup."""
    global GROUP_SELECTION_MODE, GROUP_RANGE_START, GROUP_RANGE_END, GROUP_RANDOM_COUNT, GROUP_LIST
    
    print("\n" + "=" * 60)
    print("       GROUP SELECTION")
    print("=" * 60)
    print("\nAvailable image groups:")
    print("-" * 40)
    
    for i, prefix in enumerate(IMAGE_GROUP_PREFIXES):
        print(f"  [{i}] {prefix}")
    
    print("-" * 40)
    print(f"Total groups available: {len(IMAGE_GROUP_PREFIXES)}")
    print("\nSelection options:")
    print("  r = Random selection (specify count)")
    print("  a = All groups")
    print("  Enter numbers like: 0,2,4 or 0-5")
    print("-" * 40)
    
    choice = input("Enter selection: ").strip().lower()
    
    if choice == 'r':
        count = input(f"How many random groups? (1-{len(IMAGE_GROUP_PREFIXES)}): ").strip()
        try:
            GROUP_RANDOM_COUNT = min(int(count), len(IMAGE_GROUP_PREFIXES))
            GROUP_SELECTION_MODE = "RANDOM"
            print(f"Selected: {GROUP_RANDOM_COUNT} random groups")
        except:
            GROUP_RANDOM_COUNT = 3
            GROUP_SELECTION_MODE = "RANDOM"
            print("Using default: 3 random groups")
    
    elif choice == 'a':
        GROUP_SELECTION_MODE = "RANGE"
        GROUP_RANGE_START = 0
        GROUP_RANGE_END = len(IMAGE_GROUP_PREFIXES)
        print(f"Selected: All {len(IMAGE_GROUP_PREFIXES)} groups")
    
    elif '-' in choice:
        # Range like "0-5"
        try:
            parts = choice.split('-')
            GROUP_RANGE_START = int(parts[0])
            GROUP_RANGE_END = int(parts[1]) + 1  # Make it inclusive
            GROUP_SELECTION_MODE = "RANGE"
            print(f"Selected: Groups {GROUP_RANGE_START} to {GROUP_RANGE_END - 1}")
        except:
            print("Invalid range. Using first 3 groups.")
            GROUP_RANGE_START = 0
            GROUP_RANGE_END = 3
            GROUP_SELECTION_MODE = "RANGE"
    
    elif ',' in choice:
        # List like "0,2,4"
        try:
            GROUP_LIST = [int(x.strip()) for x in choice.split(',')]
            GROUP_SELECTION_MODE = "LIST"
            print(f"Selected groups: {GROUP_LIST}")
        except:
            print("Invalid list. Using first 3 groups.")
            GROUP_LIST = [0, 1, 2]
            GROUP_SELECTION_MODE = "LIST"
    
    else:
        # Try single number or default
        try:
            single = int(choice)
            GROUP_LIST = [single]
            GROUP_SELECTION_MODE = "LIST"
            print(f"Selected group: {single}")
        except:
            print("Using default: first 3 groups")
            GROUP_RANGE_START = 0
            GROUP_RANGE_END = 3
            GROUP_SELECTION_MODE = "RANGE"


def set_version_interactive():
    """Prompt user to set version number."""
    global VERSION, GCS_OUTPUT_FOLDER
    
    print(f"\nCurrent version: {VERSION}")
    new_version = input(f"Enter new version (or press Enter to keep {VERSION}): ").strip()
    
    if new_version:
        # Clean up input - ensure it starts with 'v' if user just enters a number
        if new_version.isdigit():
            new_version = f"v{new_version}"
        elif not new_version.startswith('v'):
            new_version = f"v{new_version}"
        
        VERSION = new_version
        GCS_OUTPUT_FOLDER = f"{VERSION}_color_split"
        print(f"Version set to: {VERSION}")
    
    return VERSION


def interactive_menu():
    """Interactive menu for local testing."""
    global MODE, TEST_LIMIT, VERSION
    
    print("\n" + "=" * 60)
    print("   ECG COLOR PROCESSOR")
    print("=" * 60)
    print(f"\n  Version: {VERSION}")
    print(f"  Output:  {LOCAL_OUTPUT_FOLDER}")
    print(f"  Bucket:  {GCS_BUCKET}")
    print("-" * 60)
    print("\nCommands:")
    print("  1. Process from GCS → Save locally (select groups)")
    print("  2. Process from GCS → Save locally (random groups)")
    print("  3. Process ALL images from GCS (no group filter)")
    print("  4. Process from LOCAL folder → Save locally")
    print("  5. Scan GCS bucket (see what's there)")
    print("  6. Delete local output files")
    print("  7. Open output folder")
    print("  8. Change version / bucket")
    print("  9. Exit")
    print("-" * 60)
    
    choice = input("Enter choice (1-9): ").strip()
    
    if choice == '1':
        # GCS with group selection, save locally only
        MODE = "GCS_TO_LOCAL"
        select_groups_interactive()
        print(f"\nOutput will be saved to: {LOCAL_OUTPUT_FOLDER}")
        results = process_gcs_to_local()
        
    elif choice == '2':
        # GCS with random selection, save locally only
        MODE = "GCS_TO_LOCAL"
        count = input(f"How many random groups? (1-{len(IMAGE_GROUP_PREFIXES)}): ").strip()
        try:
            global GROUP_RANDOM_COUNT, GROUP_SELECTION_MODE
            GROUP_RANDOM_COUNT = min(int(count), len(IMAGE_GROUP_PREFIXES))
            GROUP_SELECTION_MODE = "RANDOM"
        except:
            GROUP_RANDOM_COUNT = 3
            GROUP_SELECTION_MODE = "RANDOM"
        print(f"\nSelected {GROUP_RANDOM_COUNT} random groups")
        print(f"Output will be saved to: {LOCAL_OUTPUT_FOLDER}")
        results = process_gcs_to_local()
    
    elif choice == '3':
        # Process ALL images from GCS without group filtering
        MODE = "GCS_TO_LOCAL"
        limit = input("How many images to process? (Enter number or 'all'): ").strip()
        try:
            img_limit = None if limit.lower() == 'all' else int(limit)
        except:
            img_limit = 10
        print(f"\nProcessing {'all' if img_limit is None else img_limit} images from GCS...")
        print(f"Output will be saved to: {LOCAL_OUTPUT_FOLDER}")
        results = process_gcs_all_images(img_limit)
        
    elif choice == '4':
        MODE = "LOCAL"
        print(f"\nInput/Output folder: {LOCAL_OUTPUT_FOLDER}")
        results = main()
    
    elif choice == '5':
        # Scan bucket to see what's there
        scan_bucket_contents()
    
    elif choice == '6':
        print("\nDelete options:")
        print(f"  a = All {VERSION} files in output folder")
        print("  p = Processed only (--s- files)")
        print("  k = Keepers only (--sk- files)")
        print("  m = Analysis .md files only")
        print("  o = Original copies (--original files)")
        del_choice = input("Enter choice: ").strip().lower()
        
        delete_local_files(del_choice)
    
    elif choice == '7':
        print(f"Opening: {LOCAL_OUTPUT_FOLDER}")
        try:
            os.startfile(LOCAL_OUTPUT_FOLDER)
        except:
            print(f"Could not open folder. Path: {LOCAL_OUTPUT_FOLDER}")
    
    elif choice == '8':
        print("\nSettings:")
        print("  v = Change version")
        print("  b = Change bucket")
        sub = input("Enter choice: ").strip().lower()
        if sub == 'v':
            set_version_interactive()
        elif sub == 'b':
            change_bucket_interactive()
    
    elif choice == '9':
        print("Exiting")
        return False
    
    return True


def change_bucket_interactive():
    """Allow user to change GCS bucket."""
    global GCS_BUCKET
    
    print("\nAvailable buckets:")
    print("  1. ecg-competition-data-1")
    print("  2. ecg-competition-data-2")
    print("  3. ecg-competition-data-3")
    print("  4. ecg-competition-data-4")
    print("  5. ecg-competition-data-5")
    print(f"\nCurrent: {GCS_BUCKET}")
    
    choice = input("Enter bucket number (1-5) or full name: ").strip()
    
    if choice in ['1', '2', '3', '4', '5']:
        GCS_BUCKET = f"ecg-competition-data-{choice}"
    elif choice.startswith('ecg-'):
        GCS_BUCKET = choice
    elif choice:
        GCS_BUCKET = choice
    
    print(f"Bucket set to: {GCS_BUCKET}")


def scan_bucket_contents():
    """Scan GCS bucket to see what's actually there."""
    global IMAGE_GROUP_PREFIXES
    
    print(f"\nScanning bucket: {GCS_BUCKET}")
    print("This may take a moment...")
    
    client = get_gcs_client()
    if not client:
        print("Could not connect to GCS!")
        return
    
    try:
        bucket = client.bucket(GCS_BUCKET)
        blobs = list(bucket.list_blobs(max_results=500))
        
        print(f"\nFound {len(blobs)} items in bucket (showing first 500)")
        
        # Analyze what's there
        folders = set()
        file_types = {}
        image_files = []
        prefixes = set()
        
        for blob in blobs:
            name = blob.name
            
            # Track folders
            if '/' in name:
                folder = name.split('/')[0]
                folders.add(folder)
            
            # Track file types
            ext = os.path.splitext(name)[1].lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            
            # Track image files and their prefixes
            if ext in ['.png', '.jpg', '.jpeg']:
                image_files.append(name)
                # Extract prefix (number before first dash)
                basename = os.path.basename(name)
                if '-' in basename:
                    prefix = basename.split('-')[0]
                    if prefix.isdigit():
                        prefixes.add(prefix)
        
        print(f"\nFolders found: {sorted(folders) if folders else 'None (files at root)'}")
        print(f"\nFile types:")
        for ext, count in sorted(file_types.items(), key=lambda x: -x[1]):
            print(f"  {ext or '(no extension)'}: {count}")
        
        print(f"\nImage files found: {len(image_files)}")
        print(f"Unique prefixes found: {len(prefixes)}")
        
        if image_files:
            print(f"\nSample image paths:")
            for img in image_files[:10]:
                print(f"  {img}")
        
        if prefixes:
            print(f"\nSample prefixes: {sorted(list(prefixes))[:20]}")
            
            # Offer to update IMAGE_GROUP_PREFIXES
            update = input(f"\nUpdate IMAGE_GROUP_PREFIXES with {len(prefixes)} found prefixes? (y/n): ").strip().lower()
            if update == 'y':
                IMAGE_GROUP_PREFIXES = sorted(list(prefixes))
                print(f"Updated! Now have {len(IMAGE_GROUP_PREFIXES)} groups available.")
        
        return image_files, prefixes
        
    except Exception as e:
        print(f"Error scanning bucket: {e}")
        return [], set()


def list_all_gcs_images_no_filter(bucket_name, limit=None):
    """List ALL images in GCS bucket without prefix filtering."""
    client = get_gcs_client()
    if not client:
        return []
    
    try:
        bucket = client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        
        images = []
        for blob in blobs:
            name = blob.name.lower()
            # Get any image file
            if name.endswith('.png') or name.endswith('.jpg') or name.endswith('.jpeg'):
                # Skip already processed
                if '--s-' not in name and '--sk-' not in name and '--original' not in name:
                    images.append(blob.name)
                    if limit and len(images) >= limit:
                        break
        
        return images
    except Exception as e:
        print(f"Error listing images: {e}")
        return []


if __name__ == "__main__":
    # Ensure output folder exists
    os.makedirs(LOCAL_OUTPUT_FOLDER, exist_ok=True)
    
    if ENVIRONMENT == "LOCAL":
        # Startup: Ask for version
        print("\n" + "=" * 60)
        print("   ECG COLOR PROCESSOR - STARTUP")
        print("=" * 60)
        set_version_interactive()
        
        while interactive_menu():
            pass
    else:
        main()
