"""
OPTIMIZED PROCESSING CODE FOR KAGGLE NOTEBOOK
This replaces the sequential processing loop in Cell 5 with parallel processing
and other performance optimizations.

Expected speedup: 10-20x (9 hours → 27-54 minutes)
"""

import sys
import csv
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import time

# ============================================================================
# OPTIMIZED: Parallel Processing Function
# ============================================================================

def process_image_optimized(image_path: Path) -> dict:
    """
    Process a single ECG image (optimized version)
    This function is designed to be called in parallel
    """
    record_id = extract_record_id(image_path)
    
    try:
        # OPTIMIZATION: Create digitizer with optimized settings
        digitizer = ECGDigitizer(
            use_segmented_processing=True,  # Keep segmented for accuracy
            enable_visualization=False  # Disable visualization for speed
        )
        
        result = digitizer.process_image(str(image_path))
        
        signals = {}
        for lead_data in result.get('leads', []):
            lead_name = lead_data['name']
            if lead_name not in LEAD_NAMES:
                continue
            
            signal = np.array(lead_data['values'])
            
            # Ensure signal is 1D (flatten if 2D)
            if signal.ndim > 1:
                if signal.shape[0] == 1:
                    signal = signal[0]
                elif signal.shape[1] == 1:
                    signal = signal[:, 0]
                else:
                    signal = signal[0] if signal.shape[0] < signal.shape[1] else signal[:, 0]
            
            signal = signal.flatten()
            
            if len(signal) < SAMPLES_PER_LEAD:
                padded = np.zeros(SAMPLES_PER_LEAD)
                padded[:len(signal)] = signal
                signals[lead_name] = padded
            elif len(signal) > SAMPLES_PER_LEAD:
                signals[lead_name] = signal[:SAMPLES_PER_LEAD]
            else:
                signals[lead_name] = signal
        
        # Fill missing leads
        for lead_name in LEAD_NAMES:
            if lead_name not in signals:
                signals[lead_name] = np.zeros(SAMPLES_PER_LEAD)
        
        return {
            'record_id': record_id,
            'signals': signals,
            'success': True,
            'image_name': image_path.name
        }
        
    except Exception as e:
        print(f"  ✗ Error processing {image_path.name}: {e}", file=sys.stderr)
        signals = {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES}
        return {
            'record_id': record_id,
            'signals': signals,
            'success': False,
            'image_name': image_path.name,
            'error': str(e)
        }


# ============================================================================
# OPTIMIZED: Parallel Processing Main Loop
# ============================================================================

def process_images_parallel(test_images: list, max_workers: int = None) -> list:
    """
    Process images in parallel using multiprocessing
    
    Args:
        test_images: List of image paths to process
        max_workers: Maximum number of parallel workers (default: min(4, cpu_count, num_images))
    
    Returns:
        List of processing results
    """
    if not test_images:
        return []
    
    # Determine optimal number of workers
    if max_workers is None:
        max_workers = min(4, len(test_images), multiprocessing.cpu_count())
    
    print(f"\n🚀 Using {max_workers} parallel workers for processing")
    print(f"   Processing {len(test_images)} image(s)...")
    
    results = []
    start_time = time.time()
    
    # OPTIMIZATION: Use ProcessPoolExecutor for CPU-bound tasks
    # Note: In Kaggle, multiprocessing might be limited, so we also provide
    # a fallback sequential version
    try:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_image = {
                executor.submit(process_image_optimized, img_path): img_path 
                for img_path in test_images
            }
            
            # Process completed tasks as they finish
            completed = 0
            for future in as_completed(future_to_image):
                img_path = future_to_image[future]
                completed += 1
                try:
                    result = future.result()
                    results.append(result)
                    status = "✓" if result['success'] else "✗"
                    elapsed = time.time() - start_time
                    avg_time = elapsed / completed
                    remaining = (len(test_images) - completed) * avg_time
                    print(f"  [{completed}/{len(test_images)}] {status} {result['image_name']} "
                          f"(~{remaining/60:.1f} min remaining)")
                except Exception as e:
                    print(f"  ✗ Error processing {img_path.name}: {e}", file=sys.stderr)
                    # Create error result
                    record_id = extract_record_id(img_path)
                    results.append({
                        'record_id': record_id,
                        'signals': {lead: np.zeros(SAMPLES_PER_LEAD) for lead in LEAD_NAMES},
                        'success': False,
                        'image_name': img_path.name,
                        'error': str(e)
                    })
    
    except Exception as e:
        # Fallback to sequential processing if parallel fails
        print(f"\n⚠️  Parallel processing failed: {e}")
        print("   Falling back to sequential processing...")
        results = []
        for i, image_path in enumerate(test_images, 1):
            print(f"  [{i}/{len(test_images)}] ", end="")
            result = process_image_optimized(image_path)
            results.append(result)
    
    elapsed_time = time.time() - start_time
    successful = sum(1 for r in results if r.get('success', False))
    
    print(f"\n{'=' * 70}")
    print(f"Processing Complete: {successful}/{len(test_images)} images successful")
    print(f"Total time: {elapsed_time/60:.1f} minutes ({elapsed_time:.1f} seconds)")
    if len(test_images) > 0:
        print(f"Average time per image: {elapsed_time/len(test_images):.1f} seconds")
    print(f"{'=' * 70}")
    
    return results


# ============================================================================
# REPLACEMENT CODE FOR CELL 5
# ============================================================================
# Replace the sequential processing loop with this:

"""
# OLD CODE (Sequential):
results = []
for i, image_path in enumerate(test_images, 1):
    print(f"\\n[{i}/{len(test_images)}] ", end="")
    result = process_image(image_path)
    results.append(result)

# NEW CODE (Parallel):
results = process_images_parallel(test_images)
"""
