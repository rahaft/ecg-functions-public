"""
Test Kaggle Images with SNR Calculation

This script:
1. Loads test images from Kaggle competition (train set for ground truth)
2. Processes them through the digitization pipeline
3. Loads ground truth signals from competition data
4. Calculates SNR using competition's alignment method
5. Generates submission file

Usage:
    python test_kaggle_with_snr.py [--limit N] [--record-id ID]
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from scipy import signal as sp_signal
from scipy.signal import correlate

# Add functions_python to path
sys.path.insert(0, str(Path(__file__).parent / 'functions_python'))

try:
    from digitization_pipeline import ECGDigitizer
    from evaluation import CompetitionEvaluator
    from notebook_wrapper import NotebookEnvironment, load_test_image
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import pipeline modules: {e}")
    PIPELINE_AVAILABLE = False

# Standard 12-lead ECG leads
LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
SAMPLES_PER_LEAD = 5000


def find_kaggle_images(limit: Optional[int] = None) -> List[str]:
    """
    Find Kaggle test images
    
    Args:
        limit: Maximum number of images to return
        
    Returns:
        List of image file paths
    """
    images = []
    
    # Check if running in Kaggle
    if NotebookEnvironment.is_kaggle():
        test_path = NotebookEnvironment.get_test_images_path()
        train_path = f"{NotebookEnvironment.get_input_path()}/physionet-ecg-image-digitization/train"
        
        # Try train path first (has ground truth)
        if os.path.exists(train_path):
            for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                images.extend(Path(train_path).glob(f'*{ext}'))
                images.extend(Path(train_path).glob(f'*{ext.upper()}'))
        
        # Also check test path
        if os.path.exists(test_path):
            for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                images.extend(Path(test_path).glob(f'*{ext}'))
                images.extend(Path(test_path).glob(f'*{ext.upper()}'))
    else:
        # Local testing - check common paths
        local_paths = [
            './input/physionet-ecg-image-digitization/train',
            './input/train',
            './test_images',
            './data/train'
        ]
        
        for base_path in local_paths:
            if os.path.exists(base_path):
                for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
                    images.extend(Path(base_path).glob(f'*{ext}'))
                    images.extend(Path(base_path).glob(f'*{ext.upper()}'))
                break
    
    # Convert to strings and limit
    image_paths = [str(img) for img in images]
    if limit:
        image_paths = image_paths[:limit]
    
    return image_paths


def load_ground_truth_signals(record_id: str) -> Optional[Dict[str, np.ndarray]]:
    """
    Load ground truth signals for a record
    
    Args:
        record_id: ECG record identifier (e.g., '62')
        
    Returns:
        Dictionary mapping lead names to signal arrays, or None if not found
    """
    # Ground truth is typically in train.parquet or similar
    # Format: record_id, sample_idx, lead_name, value
    
    base_path = NotebookEnvironment.get_input_path() if NotebookEnvironment.is_kaggle() else './input'
    competition_path = f"{base_path}/physionet-ecg-image-digitization"
    
    # Try different possible ground truth file locations
    gt_files = [
        f"{competition_path}/train.parquet",
        f"{competition_path}/train.csv",
        f"{competition_path}/train_labels.parquet",
        f"{base_path}/train.parquet",
        f"{base_path}/train.csv"
    ]
    
    for gt_file in gt_files:
        if os.path.exists(gt_file):
            try:
                if gt_file.endswith('.parquet'):
                    df = pd.read_parquet(gt_file)
                else:
                    df = pd.read_csv(gt_file)
                
                # Filter for this record
                # ID format might be: record_id_sample_lead or record_id, sample, lead
                if 'id' in df.columns:
                    # Parse ID format: '62_0_I' -> record=62, sample=0, lead=I
                    df['record'] = df['id'].str.extract(r"'?(\d+)_\d+_(\w+)'?")[0]
                    df['lead'] = df['id'].str.extract(r"'?(\d+)_\d+_(\w+)'?")[1]
                    df['sample'] = df['id'].str.extract(r"'?(\d+)_(\d+)_\w+'?")[1]
                    
                    record_df = df[df['record'] == str(record_id)]
                elif 'record_id' in df.columns:
                    record_df = df[df['record_id'] == record_id]
                else:
                    print(f"Warning: Unknown ground truth format in {gt_file}")
                    continue
                
                if record_df.empty:
                    continue
                
                # Group by lead and extract signals
                signals = {}
                for lead_name in LEAD_NAMES:
                    lead_data = record_df[record_df['lead'] == lead_name].sort_values('sample')
                    if not lead_data.empty and 'value' in lead_data.columns:
                        signals[lead_name] = lead_data['value'].values
                
                if signals:
                    # Ensure all signals are same length (pad/truncate to 5000)
                    for lead_name in LEAD_NAMES:
                        if lead_name in signals:
                            sig = signals[lead_name]
                            if len(sig) < SAMPLES_PER_LEAD:
                                padded = np.zeros(SAMPLES_PER_LEAD)
                                padded[:len(sig)] = sig
                                signals[lead_name] = padded
                            elif len(sig) > SAMPLES_PER_LEAD:
                                signals[lead_name] = sig[:SAMPLES_PER_LEAD]
                        else:
                            signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
                    
                    return signals
                    
            except Exception as e:
                print(f"Error loading ground truth from {gt_file}: {e}")
                continue
    
    return None


def align_signals(predicted: np.ndarray, ground_truth: np.ndarray, 
                  sampling_rate: int = 500, max_shift_sec: float = 0.2) -> Tuple[np.ndarray, float, float]:
    """
    Align predicted signal with ground truth using competition method
    
    Args:
        predicted: Predicted signal
        ground_truth: Ground truth signal
        sampling_rate: Sampling rate in Hz
        max_shift_sec: Maximum time shift in seconds
        
    Returns:
        (aligned_predicted, time_shift_sec, vertical_offset)
    """
    # Ensure same length
    min_len = min(len(predicted), len(ground_truth))
    pred = predicted[:min_len]
    gt = ground_truth[:min_len]
    
    # 1. Time alignment via cross-correlation
    max_shift_samples = int(max_shift_sec * sampling_rate)
    
    # Cross-correlate
    correlation = correlate(gt, pred, mode='full')
    mid = len(correlation) // 2
    search_range = correlation[mid - max_shift_samples:mid + max_shift_samples + 1]
    
    # Find best shift
    best_shift_idx = np.argmax(search_range)
    time_shift_samples = best_shift_idx - max_shift_samples
    
    # Apply time shift
    if time_shift_samples > 0:
        aligned_pred = np.concatenate([np.zeros(time_shift_samples), pred[:-time_shift_samples]])
    elif time_shift_samples < 0:
        aligned_pred = np.concatenate([pred[-time_shift_samples:], np.zeros(-time_shift_samples)])
    else:
        aligned_pred = pred.copy()
    
    # Ensure same length after shift
    min_len = min(len(aligned_pred), len(gt))
    aligned_pred = aligned_pred[:min_len]
    gt_aligned = gt[:min_len]
    
    # 2. Vertical alignment (remove DC offset)
    vertical_offset = np.mean(aligned_pred - gt_aligned)
    aligned_pred = aligned_pred - vertical_offset
    
    time_shift_sec = time_shift_samples / sampling_rate
    
    return aligned_pred, time_shift_sec, vertical_offset


def calculate_competition_snr(predicted_signals: Dict[str, np.ndarray],
                              ground_truth_signals: Dict[str, np.ndarray],
                              sampling_rate: int = 500) -> float:
    """
    Calculate SNR using competition's method
    
    Args:
        predicted_signals: Dictionary of predicted signals by lead
        ground_truth_signals: Dictionary of ground truth signals by lead
        sampling_rate: Sampling rate in Hz
        
    Returns:
        SNR in dB
    """
    total_signal_power = 0.0
    total_noise_power = 0.0
    
    for lead_name in LEAD_NAMES:
        if lead_name not in predicted_signals or lead_name not in ground_truth_signals:
            continue
        
        pred = predicted_signals[lead_name]
        gt = ground_truth_signals[lead_name]
        
        # Align signals
        aligned_pred, _, _ = align_signals(pred, gt, sampling_rate)
        
        # Ensure same length
        min_len = min(len(aligned_pred), len(gt))
        aligned_pred = aligned_pred[:min_len]
        gt_aligned = gt[:min_len]
        
        # Calculate powers
        signal_power = np.sum(gt_aligned ** 2)
        noise = aligned_pred - gt_aligned
        noise_power = np.sum(noise ** 2)
        
        total_signal_power += signal_power
        total_noise_power += noise_power
    
    # Calculate SNR
    if total_noise_power > 0:
        snr_db = 10 * np.log10(total_signal_power / total_noise_power)
    else:
        snr_db = 60.0  # Perfect match
    
    return float(snr_db)


def process_image_and_calculate_snr(image_path: str, record_id: Optional[str] = None) -> Dict:
    """
    Process an image and calculate SNR if ground truth available
    
    Args:
        image_path: Path to ECG image
        record_id: Optional record ID (extracted from filename if not provided)
        
    Returns:
        Dictionary with results and SNR
    """
    if not PIPELINE_AVAILABLE:
        return {'error': 'Pipeline not available'}
    
    # Extract record ID from filename if not provided
    if record_id is None:
        filename = Path(image_path).stem
        # Try to extract number from filename (e.g., "62.jpg" -> "62")
        import re
        match = re.search(r'(\d+)', filename)
        if match:
            record_id = match.group(1)
        else:
            record_id = filename
    
    print(f"\nProcessing: {image_path}")
    print(f"Record ID: {record_id}")
    
    try:
        # Initialize digitizer
        digitizer = ECGDigitizer(use_segmented_processing=True, enable_visualization=False)
        
        # Process image
        result = digitizer.process_image(image_path)
        
        # Extract signals
        predicted_signals = {}
        for lead_data in result.get('leads', []):
            lead_name = lead_data['name']
            predicted_signals[lead_name] = np.array(lead_data['values'])
            
            # Ensure correct length
            if len(predicted_signals[lead_name]) < SAMPLES_PER_LEAD:
                padded = np.zeros(SAMPLES_PER_LEAD)
                padded[:len(predicted_signals[lead_name])] = predicted_signals[lead_name]
                predicted_signals[lead_name] = padded
            elif len(predicted_signals[lead_name]) > SAMPLES_PER_LEAD:
                predicted_signals[lead_name] = predicted_signals[lead_name][:SAMPLES_PER_LEAD]
        
        # Fill missing leads with zeros
        for lead_name in LEAD_NAMES:
            if lead_name not in predicted_signals:
                predicted_signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
        
        # Load ground truth
        ground_truth_signals = load_ground_truth_signals(record_id)
        
        # Calculate SNR
        snr = None
        if ground_truth_signals:
            snr = calculate_competition_snr(predicted_signals, ground_truth_signals)
            print(f"SNR: {snr:.2f} dB")
        else:
            print("Ground truth not found - cannot calculate SNR")
        
        return {
            'record_id': record_id,
            'image_path': image_path,
            'predicted_signals': predicted_signals,
            'ground_truth_signals': ground_truth_signals,
            'snr': snr,
            'leads_extracted': len([l for l in result.get('leads', []) if l.get('values')])
        }
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'record_id': record_id, 'image_path': image_path}


def main():
    parser = argparse.ArgumentParser(
        description='Test Kaggle images with SNR calculation',
        epilog='NOTE: Test images have NO ground truth. Use TRAIN images for SNR testing.'
    )
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of images to process')
    parser.add_argument('--record-id', type=str, help='Specific record ID to process')
    parser.add_argument('--output', type=str, default='test_results.csv', help='Output CSV file')
    parser.add_argument('--use-test', action='store_true', 
                       help='Use test images (WARNING: No ground truth, SNR will not be calculated)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Kaggle Image Testing with SNR Calculation")
    print("=" * 60)
    
    if args.use_test:
        print("\n⚠️  WARNING: Using TEST images - NO ground truth available!")
        print("   SNR cannot be calculated on test images.")
        print("   Use train images (without --use-test) to calculate SNR.")
        print("   Test images are for submission only (use kaggle_submission_notebook.py)\n")
    
    # Find images (use train by default for SNR, test only if explicitly requested)
    use_train = not args.use_test
    if args.record_id:
        # Process specific record
        images = find_kaggle_images(limit=None, use_train=use_train)
        # Filter by record ID
        images = [img for img in images if args.record_id in Path(img).stem]
        if not images:
            print(f"No images found for record ID: {args.record_id}")
            return
    else:
        images = find_kaggle_images(limit=args.limit, use_train=use_train)
    
    if not images:
        print("No images found!")
        print("\nTo use this script:")
        print("⚠️  IMPORTANT: Test images have NO ground truth - cannot calculate SNR!")
        print("   Use TRAIN images for SNR testing (they have ground truth)")
        print("\n1. In Kaggle notebook: Train images in /kaggle/input/physionet-ecg-image-digitization/train/")
        print("2. Locally: Place train images in ./input/physionet-ecg-image-digitization/train/")
        print("3. Ground truth should be in train.parquet or train.csv")
        print("\nFor submission (test images): Use kaggle_submission_notebook.py")
        return
    
    print(f"\nFound {len(images)} images to process")
    
    # Process images
    results = []
    for image_path in images:
        result = process_image_and_calculate_snr(image_path, args.record_id)
        if 'error' not in result:
            results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if results:
        snr_values = [r['snr'] for r in results if r.get('snr') is not None]
        if snr_values:
            print(f"Processed: {len(results)} images")
            print(f"SNR calculated for: {len(snr_values)} images")
            print(f"Mean SNR: {np.mean(snr_values):.2f} dB")
            print(f"Min SNR: {np.min(snr_values):.2f} dB")
            print(f"Max SNR: {np.max(snr_values):.2f} dB")
        else:
            print(f"Processed: {len(results)} images")
            print("No ground truth found - SNR not calculated")
    else:
        print("No images processed successfully")
    
    # Save results
    if results:
        import csv
        with open(args.output, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['record_id', 'image_path', 'snr_db', 'leads_extracted'])
            for r in results:
                writer.writerow([
                    r.get('record_id', ''),
                    r.get('image_path', ''),
                    f"{r.get('snr', ''):.2f}" if r.get('snr') else '',
                    r.get('leads_extracted', 0)
                ])
        print(f"\nResults saved to: {args.output}")


def quick_test_single_image(image_path: str):
    """
    Quick test function for a single image (works without ground truth)
    
    Usage:
        from test_kaggle_with_snr import quick_test_single_image
        result = quick_test_single_image('path/to/image.jpg')
    """
    print(f"Quick test: {image_path}")
    
    if not PIPELINE_AVAILABLE:
        print("Error: Pipeline not available")
        return None
    
    try:
        digitizer = ECGDigitizer(use_segmented_processing=True, enable_visualization=False)
        result = digitizer.process_image(image_path)
        
        print(f"✓ Processed {len(result.get('leads', []))} leads")
        
        # Extract signals
        signals = {}
        for lead_data in result.get('leads', []):
            lead_name = lead_data['name']
            signals[lead_name] = np.array(lead_data['values'])
            print(f"  - {lead_name}: {len(signals[lead_name])} samples")
        
        return {
            'signals': signals,
            'metadata': result.get('metadata', {}),
            'leads': result.get('leads', [])
        }
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    main()

# ============================================================================
# FILE IDENTIFICATION
# ============================================================================
# This file: test_kaggle_with_snr.py
# Purpose: Test Kaggle images with SNR calculation (requires train images with ground truth)
# Usage: python test_kaggle_with_snr.py [--limit N] [--record-id ID]
# ============================================================================
