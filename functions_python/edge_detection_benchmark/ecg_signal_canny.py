"""
ECG Signal Extraction using Canny Edge Detection
Extracts clean, digitized 1D signal from scanned ECG images
"""

import numpy as np
import cv2
import sys
import os
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge_detection_benchmark.preprocessor import PreProcessor
from edge_detection_benchmark.edge_benchmarker import EdgeBenchmarker
from edge_detection_benchmark.extraction_engine import ExtractionEngine
from edge_detection_benchmark.metrics_calculator import MetricsCalculator
from edge_detection_benchmark.visualizer import Visualizer


def process_ecg_signal_canny(image_path: str, output_dir: str = None,
                            apply_skeletonization: bool = True,
                            apply_geometric_correction: bool = False) -> Dict:
    """
    Process image to extract ECG signal using Canny edge detection.
    
    Args:
        image_path: Path to input image
        output_dir: Optional output directory for saving results
        apply_skeletonization: Whether to apply skeletonization for 1-pixel-wide lines
        apply_geometric_correction: Whether to apply TPS/Affine correction
        
    Returns:
        Dictionary with processing results
    """
    # Initialize components
    preprocessor = PreProcessor(blur_kernel_size=(3, 3), blur_sigma=0)
    benchmarker = EdgeBenchmarker()
    extractor = ExtractionEngine()
    metrics_calc = MetricsCalculator()
    visualizer = Visualizer()
    
    # Load and preprocess with HSV masking for signal
    image = preprocessor.load_image(image_path)
    preprocessed = preprocessor.preprocess(
        image,
        apply_hsv_mask=True,  # Mask to isolate ECG signal
        target='signal',      # Isolate black/blue signal from red grid
        apply_adaptive_thresh=False
    )
    
    # Apply Canny edge detection (optimized for continuity)
    canny_result = benchmarker.get_canny(preprocessed['final'])
    
    # Extract signal coordinates
    signal_result = extractor.digitize_signal(
        canny_result['edges'],
        apply_skeletonization=apply_skeletonization
    )
    
    # Apply geometric correction if requested
    coordinates = signal_result['coordinates']
    if apply_geometric_correction and len(coordinates) > 0:
        # For now, skip correction (would need reference points)
        # This is a placeholder for future implementation
        pass
    
    # Calculate metrics
    metrics = metrics_calc.calculate_all_metrics(canny_result['edges'])
    
    # Prepare results
    results = {
        'method': 'canny',
        'task': 'ecg_signal_extraction',
        'image_path': image_path,
        'coordinates': coordinates,
        'num_points': signal_result['num_points'],
        'metrics': metrics,
        'edge_map': canny_result['edges'],
        'skeletonized': signal_result.get('skeletonized'),
        'params': canny_result['params']
    }
    
    # Visualize if output directory provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save edge map
        edge_path = os.path.join(output_dir, 'ecg_signal_canny_edges.png')
        cv2.imwrite(edge_path, canny_result['edges'])
        
        # Save skeletonized if available
        if signal_result.get('skeletonized') is not None:
            skeleton_path = os.path.join(output_dir, 'ecg_signal_canny_skeleton.png')
            cv2.imwrite(skeleton_path, signal_result['skeletonized'])
        
        # Create visualization
        fig = visualizer.plot_ecg_signal_extraction(
            image,
            canny_result['edges'],
            signal_result.get('skeletonized', canny_result['edges']),
            coordinates,
            method='Canny'
        )
        vis_path = os.path.join(output_dir, 'ecg_signal_canny_visualization.png')
        visualizer.save_figure(fig, vis_path)
    
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python ecg_signal_canny.py <image_path> [output_dir]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = process_ecg_signal_canny(image_path, output_dir)
    
    print("\n" + "="*60)
    print("ECG SIGNAL EXTRACTION - CANNY METHOD")
    print("="*60)
    print(f"Image: {image_path}")
    print(f"Points Extracted: {results['num_points']}")
    print(f"\nMetrics:")
    print(f"  Edge Density: {results['metrics']['edge_density']:.2f}%")
    print(f"  Line Continuity: {results['metrics']['line_continuity']:.2f}%")
    print(f"  Salt-Pepper Noise: {results['metrics']['salt_pepper_noise']:.2f}%")
    print(f"  Contours: {results['metrics']['connectivity']['num_contours']}")
    print("="*60)
