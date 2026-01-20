"""
Batch Processor Module
Processes multiple ECG images and ranks them by quality
"""

import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from tqdm import tqdm
import pandas as pd

from digitization_pipeline import ECGDigitizer
from quality_assessment import QualityAssessor


class BatchProcessor:
    """Process multiple ECG images in batch"""
    
    def __init__(self, use_segmented: bool = True, enable_visualization: bool = False):
        """
        Initialize batch processor
        
        Args:
            use_segmented: Use segmented processing
            enable_visualization: Enable line visualization
        """
        self.digitizer = ECGDigitizer(
            use_segmented_processing=use_segmented,
            enable_visualization=enable_visualization
        )
        self.quality_assessor = QualityAssessor(
            sampling_rate=self.digitizer.sampling_rate
        )
        self.results = []
    
    def process_batch(self, image_paths: List[str], 
                     output_dir: Optional[str] = None) -> List[Dict]:
        """
        Process a batch of images
        
        Args:
            image_paths: List of paths to ECG images
            output_dir: Optional directory to save results
            
        Returns:
            List of processing results
        """
        results = []
        
        for image_path in tqdm(image_paths, desc="Processing images"):
            try:
                result = self._process_single_image(image_path)
                results.append(result)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                results.append({
                    'image_path': image_path,
                    'error': str(e),
                    'success': False
                })
        
        self.results = results
        
        # Save results if output directory specified
        if output_dir:
            self._save_results(output_dir)
        
        return results
    
    def _process_single_image(self, image_path: str) -> Dict:
        """Process a single image"""
        # Process image
        result = self.digitizer.process_image(image_path)
        
        # Assess quality
        quality = self.quality_assessor.assess_quality(
            result['leads'],
            grid_info=getattr(self.digitizer, 'last_grid_info', None)
        )
        
        return {
            'image_path': image_path,
            'image_name': os.path.basename(image_path),
            'success': True,
            'leads': result['leads'],
            'metadata': result['metadata'],
            'quality': quality
        }
    
    def rank_by_quality(self, results: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Rank images by quality score
        
        Args:
            results: Optional list of results (uses self.results if None)
            
        Returns:
            Sorted list of results (best first)
        """
        if results is None:
            results = self.results
        
        # Filter successful results
        successful = [r for r in results if r.get('success', False)]
        
        # Sort by overall quality score
        ranked = sorted(
            successful,
            key=lambda x: x.get('quality', {}).get('overall_score', 0.0),
            reverse=True
        )
        
        return ranked
    
    def get_best_images(self, n: int = 10, 
                       results: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Get top N best quality images
        
        Args:
            n: Number of images to return
            results: Optional list of results
            
        Returns:
            List of top N results
        """
        ranked = self.rank_by_quality(results)
        return ranked[:n]
    
    def generate_quality_report(self, output_path: str, 
                               results: Optional[List[Dict]] = None):
        """
        Generate a quality report CSV
        
        Args:
            output_path: Path to save CSV report
            results: Optional list of results
        """
        if results is None:
            results = self.results
        
        # Extract metrics for each image
        report_data = []
        for result in results:
            if not result.get('success', False):
                continue
            
            quality = result.get('quality', {})
            snr = quality.get('snr', {})
            grid_quality = quality.get('grid_quality', {})
            signal_clarity = quality.get('signal_clarity', {})
            completeness = quality.get('completeness', {})
            
            report_data.append({
                'image_name': result.get('image_name', ''),
                'image_path': result.get('image_path', ''),
                'overall_score': quality.get('overall_score', 0.0),
                'mean_snr': snr.get('mean_snr', 0.0),
                'min_snr': snr.get('min_snr', 0.0),
                'grid_score': grid_quality.get('grid_score', 0.0) if grid_quality else 0.0,
                'clarity_score': signal_clarity.get('clarity_score', 0.0),
                'completeness_score': completeness.get('overall_completeness', 0.0),
                'num_leads': completeness.get('num_leads', 0),
                'valid_leads': completeness.get('valid_leads', 0)
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(report_data)
        df = df.sort_values('overall_score', ascending=False)
        df.to_csv(output_path, index=False)
        
        return df
    
    def _save_results(self, output_dir: str):
        """Save processing results to output directory"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save full results as JSON
        results_path = os.path.join(output_dir, 'batch_results.json')
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate quality report
        report_path = os.path.join(output_dir, 'quality_report.csv')
        self.generate_quality_report(report_path)
        
        # Save best images list
        best_images = self.get_best_images(10)
        best_path = os.path.join(output_dir, 'best_images.json')
        with open(best_path, 'w') as f:
            json.dump(best_images, f, indent=2, default=str)
        
        print(f"Results saved to {output_dir}")
        print(f"  - Full results: {results_path}")
        print(f"  - Quality report: {report_path}")
        print(f"  - Best images: {best_path}")
