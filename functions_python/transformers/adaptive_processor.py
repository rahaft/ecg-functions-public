"""
Adaptive Processing Pipeline Orchestrator
3-tier fallback strategy with automatic method selection

Pipeline Logic:
- Attempt 1: Standard Pipeline (fast)
- Attempt 2: LAB + CLAHE Pipeline (colored grids)
- Attempt 3: FFT Reconstruction (damaged)
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional

# Import preprocessing modules
from .quality_gates import QualityGates
from .color_separation import ColorSeparator
from .illumination_normalization import IlluminationNormalizer
from .multi_scale_grid_detector import MultiScaleGridDetector
from .fft_grid_reconstruction import FFTGridReconstructor


class AdaptiveProcessor:
    """
    Adaptive Processing Pipeline for ECG Images
    
    Purpose: Intelligent method selection with 3-tier fallback strategy
    """
    
    def __init__(self):
        """Initialize Adaptive Processor"""
        self.quality_gates = QualityGates()
        self.color_separator_lab = ColorSeparator(method='lab')
        self.color_separator_hsv = ColorSeparator(method='hsv')
        self.illumination_normalizer = IlluminationNormalizer(method='clahe')
        self.grid_detector = MultiScaleGridDetector()
        self.fft_reconstructor = FFTGridReconstructor()
        
        # Quality thresholds
        self.EXCELLENT_SCORE = 0.9
        self.GOOD_SCORE = 0.7
        self.FAIR_SCORE = 0.5
        self.POOR_SCORE = 0.3
    
    def process(self, image: np.ndarray, mode: str = 'auto') -> Dict:
        """
        Process image with adaptive pipeline
        
        Args:
            image: Input image
            mode: 'auto' (default), 'test' (step-by-step), or 'production' (automatic)
            
        Returns:
            Dictionary with processing results and selected method
        """
        # Step 0: Quality Gates
        quality_check = self.quality_gates.check_all(image)
        
        if not quality_check['passed']:
            return {
                'success': False,
                'reason': 'Quality gates failed',
                'quality_check': quality_check,
                'attempts': []
            }
        
        results = []
        
        # Attempt 1: Standard Pipeline
        result1 = self._attempt_standard(image)
        score1 = self._calculate_grid_quality(result1)
        results.append({
            'attempt': 1,
            'method': 'standard',
            'result': result1,
            'score': score1,
            'success': score1 >= self.GOOD_SCORE
        })
        
        if score1 >= self.EXCELLENT_SCORE:
            return {
                'success': True,
                'method': 'standard',
                'score': score1,
                'result': result1,
                'quality_check': quality_check,
                'attempts': results
            }
        
        # Attempt 2: LAB + CLAHE Pipeline
        if score1 < self.GOOD_SCORE:
            result2 = self._attempt_lab_clahe(image)
            score2 = self._calculate_grid_quality(result2)
            results.append({
                'attempt': 2,
                'method': 'lab_clahe',
                'result': result2,
                'score': score2,
                'success': score2 >= self.FAIR_SCORE
            })
            
            if score2 >= self.FAIR_SCORE:
                return {
                    'success': True,
                    'method': 'lab_clahe',
                    'score': score2,
                    'result': result2,
                    'quality_check': quality_check,
                    'attempts': results
                }
        
        # Attempt 3: FFT Reconstruction
        if score1 < self.FAIR_SCORE or (len(results) > 1 and results[1]['score'] < self.FAIR_SCORE):
            result3 = self._attempt_fft(image)
            score3 = self._calculate_grid_quality(result3)
            results.append({
                'attempt': 3,
                'method': 'fft',
                'result': result3,
                'score': score3,
                'success': score3 >= self.POOR_SCORE
            })
            
            if score3 >= self.POOR_SCORE:
                return {
                    'success': True,
                    'method': 'fft',
                    'score': score3,
                    'result': result3,
                    'quality_check': quality_check,
                    'attempts': results
                }
        
        # All attempts failed - return best result
        best_attempt = max(results, key=lambda x: x['score'])
        
        if best_attempt['score'] < self.POOR_SCORE:
            return {
                'success': False,
                'reason': 'All methods failed - manual review needed',
                'best_method': best_attempt['method'],
                'best_score': best_attempt['score'],
                'best_result': best_attempt['result'],
                'quality_check': quality_check,
                'attempts': results
            }
        
        return {
            'success': True,
            'method': best_attempt['method'],
            'score': best_attempt['score'],
            'result': best_attempt['result'],
            'quality_check': quality_check,
            'attempts': results,
            'warning': 'Best result is below ideal quality'
        }
    
    def _attempt_standard(self, image: np.ndarray) -> Dict:
        """
        Attempt 1: Standard Pipeline
        
        Process:
        - Grayscale conversion
        - Morphological filtering
        - Standard grid detection
        
        Args:
            image: Input image
            
        Returns:
            Processing result dictionary
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Basic morphological operations
        # Detect grid lines
        grid_result = self.grid_detector.detect(gray)
        
        return {
            'preprocessed_image': gray,
            'grid_detection': grid_result,
            'method': 'standard'
        }
    
    def _attempt_lab_clahe(self, image: np.ndarray) -> Dict:
        """
        Attempt 2: LAB + CLAHE Pipeline
        
        Process:
        - LAB color separation
        - CLAHE contrast boost
        - Morphological filtering
        
        Args:
            image: Input image
            
        Returns:
            Processing result dictionary
        """
        # Step 1: Color separation (LAB)
        color_result = self.color_separator_lab.separate(image, grid_color='auto')
        
        # Step 2: Illumination normalization (CLAHE)
        illum_result = self.illumination_normalizer.normalize(
            color_result['trace_image'],
            clip_limit=2.0,
            tile_grid_size=(8, 8)
        )
        
        # Step 3: Grid detection
        grid_result = self.grid_detector.detect(illum_result['normalized_image'])
        
        return {
            'preprocessed_image': illum_result['normalized_image'],
            'color_separation': color_result,
            'illumination_normalization': illum_result,
            'grid_detection': grid_result,
            'method': 'lab_clahe'
        }
    
    def _attempt_fft(self, image: np.ndarray) -> Dict:
        """
        Attempt 3: FFT Reconstruction
        
        Process:
        - FFT analysis
        - Grid reconstruction
        - Frequency filtering
        
        Args:
            image: Input image
            
        Returns:
            Processing result dictionary
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # FFT reconstruction
        fft_result = self.fft_reconstructor.reconstruct(gray)
        
        return {
            'preprocessed_image': fft_result['reconstructed_grid'],
            'fft_reconstruction': fft_result,
            'method': 'fft'
        }
    
    def _calculate_grid_quality(self, result: Dict) -> float:
        """
        Calculate grid quality score
        
        Args:
            result: Processing result dictionary
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        # Extract grid detection info
        if 'grid_detection' in result:
            grid = result['grid_detection']
            
            # Calculate score based on:
            # - Number of detected lines
            # - Grid validation status
            
            total_lines = grid.get('combined_grid', {}).get('total_lines', 0)
            validation = grid.get('validation', {})
            
            # Normalize score
            line_score = min(total_lines / 20.0, 1.0)  # Max 20 lines = 1.0
            
            validation_score = 1.0 if validation.get('valid', False) else 0.5
            
            # Combined score
            score = (line_score * 0.7 + validation_score * 0.3)
            
            return float(score)
        
        elif 'fft_reconstruction' in result:
            # FFT reconstruction quality
            validation = result['fft_reconstruction'].get('validation', {})
            if validation.get('valid', False):
                return 0.6  # FFT is fallback, so lower base score
            return 0.3
        
        # Fallback: no grid detection info
        return 0.1


# Convenience function
def process_adaptive(image: np.ndarray, mode: str = 'auto') -> Dict:
    """
    Convenience function for adaptive processing
    
    Args:
        image: Input image
        mode: 'auto' (default), 'test', or 'production'
        
    Returns:
        Processing results
    """
    processor = AdaptiveProcessor()
    return processor.process(image, mode)
