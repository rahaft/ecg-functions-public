"""
Document Boundary Detection using Sobel Edge Detection
Extracts 4-corner document boundaries from scanned ECG images
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


def process_document_sobel(image_path: str, output_dir: str = None) -> Dict:
    """
    Process image to extract document boundaries using Sobel edge detection.
    
    Args:
        image_path: Path to input image
        output_dir: Optional output directory for saving results
        
    Returns:
        Dictionary with processing results
    """
    # Initialize components
    preprocessor = PreProcessor(blur_kernel_size=(3, 3), blur_sigma=0)
    benchmarker = EdgeBenchmarker()
    extractor = ExtractionEngine()
    metrics_calc = MetricsCalculator()
    visualizer = Visualizer()
    
    # Load and preprocess
    image = preprocessor.load_image(image_path)
    preprocessed = preprocessor.preprocess(
        image,
        apply_hsv_mask=False,  # Don't mask for document detection
        apply_adaptive_thresh=False
    )
    
    # Apply Sobel edge detection
    sobel_result = benchmarker.get_sobel(preprocessed['final'])
    
    # Find document boundaries
    doc_result = extractor.find_document(sobel_result['edges'])
    
    # Calculate metrics
    metrics = metrics_calc.calculate_all_metrics(sobel_result['edges'])
    
    # Prepare results
    results = {
        'method': 'sobel',
        'task': 'document_boundary',
        'image_path': image_path,
        'document_found': doc_result['found'],
        'corners': doc_result['corners'],
        'document_area': doc_result['area'],
        'metrics': metrics,
        'edge_map': sobel_result['edges'],
        'params': sobel_result['params']
    }
    
    # Visualize if output directory provided
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save edge map
        edge_path = os.path.join(output_dir, 'document_sobel_edges.png')
        cv2.imwrite(edge_path, sobel_result['edges'])
        
        # Create visualization
        if doc_result['corners']:
            fig = visualizer.plot_document_extraction(
                image,
                sobel_result['edges'],
                doc_result['corners'],
                method='Sobel'
            )
            vis_path = os.path.join(output_dir, 'document_sobel_visualization.png')
            visualizer.save_figure(fig, vis_path)
    
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python document_sobel.py <image_path> [output_dir]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = process_document_sobel(image_path, output_dir)
    
    print("\n" + "="*60)
    print("DOCUMENT BOUNDARY DETECTION - SOBEL METHOD")
    print("="*60)
    print(f"Image: {image_path}")
    print(f"Document Found: {results['document_found']}")
    if results['corners']:
        print(f"Corners: {results['corners']}")
        print(f"Document Area: {results['document_area']} pixels")
    print(f"\nMetrics:")
    print(f"  Edge Density: {results['metrics']['edge_density']:.2f}%")
    print(f"  Contours: {results['metrics']['connectivity']['num_contours']}")
    print(f"  Salt-Pepper Noise: {results['metrics']['salt_pepper_noise']:.2f}%")
    print("="*60)
