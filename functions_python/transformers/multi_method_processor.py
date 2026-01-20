"""
Multi-Method Transformation Processor
Applies all transformation methods and compares results
"""

import numpy as np
from typing import Dict, List, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

from .barrel_transformer import BarrelTransformer
from .polynomial_transformer import PolynomialTransformer
# TODO: Add TPS and Perspective transformers
# from .tps_transformer import TPSTransformer
# from .perspective_transformer import PerspectiveTransformer


class MultiMethodProcessor:
    """
    Processes ECG images with multiple transformation methods
    and selects the best one based on quality scores.
    """
    
    def __init__(self):
        self.transformers = {
            'barrel': BarrelTransformer(),
            'polynomial': PolynomialTransformer(),
            # 'tps': TPSTransformer(),
            # 'perspective': PerspectiveTransformer()
        }
    
    def process_all_methods(self, image: np.ndarray, timeout: int = 120) -> Dict:
        """
        Apply all transformation methods in parallel and compare results.
        
        Args:
            image: Input ECG image
            timeout: Maximum time per method (seconds)
            
        Returns:
            Dictionary with results from all methods and best method selection
        """
        results = {}
        start_time = time.time()
        
        # Process each method
        for method_name, transformer in self.transformers.items():
            try:
                method_start = time.time()
                
                # Apply transformation
                result = transformer.transform(image)
                
                method_time = time.time() - method_start
                
                results[method_name] = {
                    **result,
                    'processing_time': method_time,
                    'success': True
                }
                
            except Exception as e:
                results[method_name] = {
                    'success': False,
                    'error': str(e),
                    'processing_time': time.time() - method_start if 'method_start' in locals() else 0
                }
        
        total_time = time.time() - start_time
        
        # Rank methods by quality
        rankings = self._rank_methods(results)
        
        # Select best method
        best_method = rankings[0]['method'] if rankings else None
        
        return {
            'results': results,
            'rankings': rankings,
            'best_method': best_method,
            'total_processing_time': total_time,
            'methods_tested': list(self.transformers.keys())
        }
    
    def _rank_methods(self, results: Dict) -> List[Dict]:
        """
        Rank transformation methods by combined quality score.
        
        Scoring weights:
        - 30% Geometric metrics (RMSE, orthogonality, aspect ratio)
        - 70% Signal metrics (SNR, SSIM, smoothness, R²)
        """
        rankings = []
        
        for method_name, result in results.items():
            if not result.get('success', False):
                continue
            
            metrics = result.get('metrics', {})
            
            # Geometric scores (normalized to 0-1)
            rmse = metrics.get('rmse', float('inf'))
            rmse_score = max(0, 1 - (rmse / 10))  # 10px = 0, 0px = 1
            
            r2 = metrics.get('r2', 0.0)
            
            # Combined geometric score (30% weight)
            geometric_score = 0.4 * rmse_score + 0.6 * r2
            
            # Signal scores (70% weight) - simplified for now
            # In full implementation, would calculate SNR, SSIM, etc.
            signal_score = r2  # Placeholder
            
            # Combined score
            combined_score = 0.3 * geometric_score + 0.7 * signal_score
            
            rankings.append({
                'method': method_name,
                'combined_score': combined_score,
                'geometric_score': geometric_score,
                'signal_score': signal_score,
                'r2': r2,
                'rmse': rmse,
                'quality': metrics.get('quality', 'unknown'),
                'processing_time': result.get('processing_time', 0)
            })
        
        # Sort by combined score (descending)
        rankings.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return rankings
    
    def get_best_result(self, multi_result: Dict) -> Optional[Dict]:
        """Extract the best transformation result."""
        best_method = multi_result.get('best_method')
        if not best_method:
            return None
        
        return multi_result['results'].get(best_method)
