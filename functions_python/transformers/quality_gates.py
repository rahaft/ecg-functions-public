"""
Quality Gates System
Automatic image quality assessment before processing

Checks:
1. Blur Detection (Laplacian variance)
2. Resolution Check (DPI estimation)
3. Contrast Analysis (Histogram standard deviation)
4. Grid Detectability Test
"""

import numpy as np
import cv2
from typing import Dict, Tuple, Optional
from scipy import ndimage


class QualityGates:
    """
    Quality Gates System for ECG image validation
    
    Purpose: Catch bad images early and provide specific feedback
    """
    
    # Quality thresholds
    BLUR_THRESHOLD = 100  # Laplacian variance
    MIN_DPI = 150  # Minimum DPI required
    MIN_CONTRAST_STD = 30  # Minimum histogram standard deviation
    MIN_GRID_LINES = 5  # Minimum grid lines detected
    
    def __init__(self, blur_threshold: int = None, min_dpi: int = None, 
                 min_contrast_std: int = None, min_grid_lines: int = None):
        """
        Initialize Quality Gates
        
        Args:
            blur_threshold: Minimum Laplacian variance (default: 100)
            min_dpi: Minimum DPI required (default: 150)
            min_contrast_std: Minimum contrast standard deviation (default: 30)
            min_grid_lines: Minimum grid lines to detect (default: 5)
        """
        self.blur_threshold = blur_threshold or QualityGates.BLUR_THRESHOLD
        self.min_dpi = min_dpi or QualityGates.MIN_DPI
        self.min_contrast_std = min_contrast_std or QualityGates.MIN_CONTRAST_STD
        self.min_grid_lines = min_grid_lines or QualityGates.MIN_GRID_LINES
    
    def check_all(self, image: np.ndarray, image_width_px: int = None, 
                  image_height_px: int = None, image_width_mm: float = None) -> Dict:
        """
        Run all quality checks
        
        Args:
            image: Input image (numpy array)
            image_width_px: Image width in pixels (optional, for DPI calculation)
            image_height_px: Image height in pixels (optional, for DPI calculation)
            image_width_mm: Expected image width in mm (optional, for DPI calculation)
            
        Returns:
            Dictionary with check results and overall pass/fail status
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        results = {}
        
        # 1. Blur Detection
        blur_result = self.check_blur(gray)
        results['blur'] = blur_result
        
        # 2. Resolution Check
        resolution_result = self.check_resolution(
            gray, image_width_px, image_height_px, image_width_mm
        )
        results['resolution'] = resolution_result
        
        # 3. Contrast Analysis
        contrast_result = self.check_contrast(gray)
        results['contrast'] = contrast_result
        
        # 4. Grid Detectability Test (preliminary)
        grid_result = self.test_grid_detectability(gray)
        results['grid_detectability'] = grid_result
        
        # Overall status
        passed = (
            blur_result['passed'] and 
            resolution_result['passed'] and
            contrast_result['passed'] and
            grid_result['detected_lines'] >= self.min_grid_lines
        )
        
        warnings = []
        if not blur_result['passed']:
            warnings.append(f"Blur check failed: {blur_result['message']}")
        if not resolution_result['passed']:
            warnings.append(f"Resolution check failed: {resolution_result['message']}")
        if contrast_result['passed'] and contrast_result['warning']:
            warnings.append(f"Contrast warning: {contrast_result['message']}")
        if grid_result['detected_lines'] < self.min_grid_lines:
            warnings.append(f"Grid detectability low: {grid_result['message']}")
        
        return {
            'passed': passed,
            'warnings': warnings,
            'results': results,
            'recommendation': self._get_recommendation(results, passed)
        }
    
    def check_blur(self, image: np.ndarray) -> Dict:
        """
        Check image blur using Laplacian variance
        
        Laplacian variance < 100: Too blurry
        Laplacian variance >= 100: Acceptable
        
        Args:
            image: Grayscale image
            
        Returns:
            Dictionary with blur check results
        """
        # Calculate Laplacian variance
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        variance = laplacian.var()
        
        passed = variance >= self.blur_threshold
        
        return {
            'passed': passed,
            'variance': float(variance),
            'threshold': self.blur_threshold,
            'message': 'Image too blurry - please rescan with higher quality' if not passed 
                      else f'Blur check passed (variance: {variance:.2f})',
            'quality': 'good' if variance > 200 else 'fair' if passed else 'poor'
        }
    
    def check_resolution(self, image: np.ndarray, width_px: int = None, 
                        height_px: int = None, width_mm: float = None) -> Dict:
        """
        Check image resolution (DPI estimation)
        
        DPI < 150: REJECT
        DPI 150-200: WARN
        DPI >= 200: PASS
        
        Args:
            image: Grayscale image
            width_px: Image width in pixels
            height_px: Image height in pixels
            width_mm: Expected image width in mm (for ECG: typically ~210mm)
            
        Returns:
            Dictionary with resolution check results
        """
        h, w = image.shape[:2]
        
        # If dimensions provided, use them
        if width_px:
            w = width_px
        if height_px:
            h = height_px
        
        # Estimate DPI
        # Standard ECG paper is 210mm wide
        # If we know width in mm, calculate DPI
        if width_mm:
            dpi = (w / width_mm) * 25.4  # Convert mm to inches
        else:
            # Estimate based on typical ECG dimensions
            # Assume standard ECG width ~210mm
            assumed_width_mm = 210
            dpi = (w / assumed_width_mm) * 25.4
        
        passed = dpi >= self.min_dpi
        warning = 150 <= dpi < 200
        
        quality = 'excellent' if dpi >= 300 else 'good' if dpi >= 200 else 'fair' if passed else 'poor'
        
        return {
            'passed': passed,
            'dpi': float(dpi),
            'threshold': self.min_dpi,
            'warning': warning,
            'message': 'Resolution too low - minimum 150 DPI required' if not passed 
                      else f'Low resolution - accuracy reduced (DPI: {dpi:.1f})' if warning
                      else f'Resolution check passed (DPI: {dpi:.1f})',
            'quality': quality
        }
    
    def check_contrast(self, image: np.ndarray) -> Dict:
        """
        Check image contrast using histogram standard deviation
        
        Std < 30: WARN/REJECT (depends on use case - final rejection happens at end)
        Std 30-50: WARN (use CLAHE boost)
        Std > 50: PASS
        
        Args:
            image: Grayscale image
            
        Returns:
            Dictionary with contrast check results
        """
        # Calculate histogram
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        
        # Calculate standard deviation
        mean = np.mean(hist)
        std = np.std(hist)
        
        passed = std >= self.min_contrast_std
        warning = self.min_contrast_std <= std < 50
        
        quality = 'excellent' if std > 50 else 'good' if std > 35 else 'fair' if passed else 'poor'
        
        recommendation = None
        if not passed:
            recommendation = 'Apply CLAHE contrast enhancement or rescan with better lighting'
        elif warning:
            recommendation = 'Consider applying CLAHE contrast boost for better results'
        
        return {
            'passed': passed,
            'std': float(std),
            'threshold': self.min_contrast_std,
            'warning': warning,
            'message': 'Low contrast - insufficient detail' if not passed
                      else f'Poor contrast - consider using CLAHE boost (Std: {std:.2f})' if warning
                      else f'Contrast check passed (Std: {std:.2f})',
            'quality': quality,
            'recommendation': recommendation
        }
    
    def test_grid_detectability(self, image: np.ndarray) -> Dict:
        """
        Test if grid lines can be detected
        
        Purpose: Preliminary check to route to appropriate method
        
        Args:
            image: Grayscale image
            
        Returns:
            Dictionary with grid detectability results
        """
        # Simple Hough line detection test
        # Use Canny edge detection
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                minLineLength=image.shape[1]//4, maxLineGap=10)
        
        horizontal_lines = []
        vertical_lines = []
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Classify as horizontal or vertical
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                
                if angle < 15 or angle > 165:  # Horizontal
                    horizontal_lines.append(line[0])
                elif 75 < angle < 105:  # Vertical
                    vertical_lines.append(line[0])
        
        total_lines = len(horizontal_lines) + len(vertical_lines)
        detected_lines = total_lines
        
        # Determine status
        if detected_lines == 0:
            status = 'none'
            recommendation = 'Try FFT method for grid reconstruction'
        elif detected_lines < self.min_grid_lines:
            status = 'partial'
            recommendation = 'Partial grid detected - consider FFT method'
        else:
            status = 'sufficient'
            recommendation = 'Grid detection should work with standard methods'
        
        return {
            'detected_lines': detected_lines,
            'horizontal_lines': len(horizontal_lines),
            'vertical_lines': len(vertical_lines),
            'status': status,
            'message': f'Detected {detected_lines} grid lines ({len(horizontal_lines)} horizontal, {len(vertical_lines)} vertical)',
            'recommendation': recommendation,
            'threshold': self.min_grid_lines
        }
    
    def _get_recommendation(self, results: Dict, passed: bool) -> str:
        """
        Generate overall recommendation based on check results
        
        Args:
            results: All check results
            passed: Overall pass status
            
        Returns:
            Recommendation string
        """
        if passed:
            return 'All quality checks passed - proceed with standard pipeline'
        
        # Build recommendation based on failures
        recommendations = []
        
        if not results['blur']['passed']:
            recommendations.append('Rescan image with higher quality scanner or camera')
        
        if not results['resolution']['passed']:
            recommendations.append('Use higher resolution scan (minimum 150 DPI)')
        
        if not results['contrast']['passed']:
            recommendations.append('Apply CLAHE contrast enhancement or rescan with better lighting')
        
        if results['grid_detectability']['detected_lines'] < self.min_grid_lines:
            recommendations.append('Try FFT-based grid reconstruction method')
        
        if recommendations:
            return ' | '.join(recommendations)
        
        return 'Proceed with standard pipeline'


# Convenience function
def check_image_quality(image: np.ndarray, **kwargs) -> Dict:
    """
    Convenience function to check image quality
    
    Args:
        image: Input image
        **kwargs: Additional arguments for quality gates
        
    Returns:
        Quality check results
    """
    gates = QualityGates()
    return gates.check_all(image, **kwargs)
