"""
Complete Edge Detection Benchmarking Suite
Compares all three methods (Canny, Sobel, Laplacian) for both document and ECG signal tasks
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

# Import individual processors
from edge_detection_benchmark.document_canny import process_document_canny
from edge_detection_benchmark.document_sobel import process_document_sobel
from edge_detection_benchmark.document_laplacian import process_document_laplacian
from edge_detection_benchmark.ecg_signal_canny import process_ecg_signal_canny
from edge_detection_benchmark.ecg_signal_sobel import process_ecg_signal_sobel
from edge_detection_benchmark.ecg_signal_laplacian import process_ecg_signal_laplacian


def benchmark_all_methods(image_path: str, output_dir: str = None) -> Dict:
    """
    Run complete benchmark comparing all methods for both tasks.
    
    Args:
        image_path: Path to input image
        output_dir: Optional output directory for saving results
        
    Returns:
        Dictionary with all benchmark results
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        doc_dir = os.path.join(output_dir, 'document_detection')
        ecg_dir = os.path.join(output_dir, 'ecg_signal_extraction')
    else:
        doc_dir = None
        ecg_dir = None
    
    results = {
        'image_path': image_path,
        'document_detection': {},
        'ecg_signal_extraction': {}
    }
    
    print("\n" + "="*80)
    print("EDGE DETECTION BENCHMARKING SUITE")
    print("="*80)
    print(f"Image: {image_path}\n")
    
    # Document Detection Benchmarks
    print("="*80)
    print("TASK 1: DOCUMENT BOUNDARY DETECTION")
    print("="*80)
    
    print("\n[1/3] Running Canny method...")
    results['document_detection']['canny'] = process_document_canny(image_path, doc_dir)
    
    print("\n[2/3] Running Sobel method...")
    results['document_detection']['sobel'] = process_document_sobel(image_path, doc_dir)
    
    print("\n[3/3] Running Laplacian method...")
    results['document_detection']['laplacian'] = process_document_laplacian(image_path, doc_dir)
    
    # ECG Signal Extraction Benchmarks
    print("\n" + "="*80)
    print("TASK 2: ECG SIGNAL EXTRACTION")
    print("="*80)
    
    print("\n[1/3] Running Canny method...")
    results['ecg_signal_extraction']['canny'] = process_ecg_signal_canny(image_path, ecg_dir)
    
    print("\n[2/3] Running Sobel method...")
    results['ecg_signal_extraction']['sobel'] = process_ecg_signal_sobel(image_path, ecg_dir)
    
    print("\n[3/3] Running Laplacian method...")
    results['ecg_signal_extraction']['laplacian'] = process_ecg_signal_laplacian(image_path, ecg_dir)
    
    # Comparison Analysis
    print("\n" + "="*80)
    print("COMPARISON ANALYSIS")
    print("="*80)
    
    # Document Detection Comparison
    print("\n--- DOCUMENT BOUNDARY DETECTION ---")
    doc_metrics = {}
    for method, result in results['document_detection'].items():
        doc_metrics[method] = result['metrics']
    
    metrics_calc = MetricsCalculator()
    metrics_calc.print_comparison_table(doc_metrics)
    
    # ECG Signal Comparison
    print("\n--- ECG SIGNAL EXTRACTION ---")
    ecg_metrics = {}
    for method, result in results['ecg_signal_extraction'].items():
        ecg_metrics[method] = result['metrics']
    
    metrics_calc.print_comparison_table(ecg_metrics)
    
    # Create combined visualization
    if output_dir:
        visualizer = Visualizer()
        
        # Load original image
        image = cv2.imread(image_path)
        
        # Document detection comparison
        doc_canny = results['document_detection']['canny']
        doc_sobel = results['document_detection']['sobel']
        doc_laplacian = results['document_detection']['laplacian']
        
        fig = visualizer.plot_comparison_grid(
            image,
            {'edges': doc_canny['edge_map']},
            {'edges': doc_sobel['edge_map']},
            {'edges': doc_laplacian['edge_map']},
            title="Document Boundary Detection - Method Comparison"
        )
        vis_path = os.path.join(output_dir, 'document_comparison.png')
        visualizer.save_figure(fig, vis_path)
        
        # ECG signal comparison
        ecg_canny = results['ecg_signal_extraction']['canny']
        ecg_sobel = results['ecg_signal_extraction']['sobel']
        ecg_laplacian = results['ecg_signal_extraction']['laplacian']
        
        fig = visualizer.plot_comparison_grid(
            image,
            {'edges': ecg_canny['edge_map']},
            {'edges': ecg_sobel['edge_map']},
            {'edges': ecg_laplacian['edge_map']},
            title="ECG Signal Extraction - Method Comparison"
        )
        vis_path = os.path.join(output_dir, 'ecg_signal_comparison.png')
        visualizer.save_figure(fig, vis_path)
    
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python benchmark_all.py <image_path> [output_dir]")
        print("\nThis script will:")
        print("  1. Run all 3 methods for document boundary detection")
        print("  2. Run all 3 methods for ECG signal extraction")
        print("  3. Compare results and generate visualizations")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'benchmark_output'
    
    results = benchmark_all_methods(image_path, output_dir)
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETE")
    print("="*80)
    if output_dir:
        print(f"Results saved to: {output_dir}")
    print("="*80)
