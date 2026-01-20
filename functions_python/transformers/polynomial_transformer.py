"""
4th Order Polynomial Transform
Fits 4th degree polynomials to grid lines for smooth distortion correction
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple
from scipy.optimize import curve_fit
from .base_transformer import BaseTransformer


class PolynomialTransformer(BaseTransformer):
    """
    Corrects distortions using 4th degree polynomial fitting to grid lines.
    """
    
    def __init__(self):
        super().__init__('polynomial')
        self.polynomial_degree = 4
        
    def detect_grid(self, image: np.ndarray) -> Dict:
        """Detect grid lines (reuse from barrel transformer for now)."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            red_channel = image[:, :, 2]
            green_channel = image[:, :, 1]
            blue_channel = image[:, :, 0]
            red_mask = (red_channel > 200) & (red_channel > green_channel * 1.5) & (red_channel > blue_channel * 1.5)
            grid_mask = red_mask.astype(np.uint8) * 255
        else:
            gray = image.copy()
            edges = cv2.Canny(gray, 50, 150)
            grid_mask = edges
        
        # Detect lines
        horizontal_lines = cv2.HoughLinesP(
            grid_mask, 1, np.pi/180, threshold=100,
            minLineLength=image.shape[1]//4, maxLineGap=10
        )
        
        vertical_lines = cv2.HoughLinesP(
            cv2.rotate(grid_mask, cv2.ROTATE_90_CLOCKWISE), 1, np.pi/180, threshold=100,
            minLineLength=image.shape[0]//4, maxLineGap=10
        )
        
        if vertical_lines is not None:
            for line in vertical_lines:
                x1, y1, x2, y2 = line[0]
                line[0] = [y1, image.shape[1] - x1, y2, image.shape[1] - x2]
        
        intersections = self._find_intersections(
            horizontal_lines if horizontal_lines is not None else [],
            vertical_lines if vertical_lines is not None else [],
            image.shape
        )
        
        return {
            'horizontal_lines': horizontal_lines.tolist() if horizontal_lines is not None else [],
            'vertical_lines': vertical_lines.tolist() if vertical_lines is not None else [],
            'intersections': intersections,
            'image_shape': image.shape
        }
    
    def _find_intersections(self, horizontal_lines: List, vertical_lines: List, image_shape: Tuple) -> List:
        """Find intersection points."""
        intersections = []
        for h_line in horizontal_lines:
            x1_h, y1_h, x2_h, y2_h = h_line[0]
            y_h = (y1_h + y2_h) / 2
            for v_line in vertical_lines:
                x1_v, y1_v, x2_v, y2_v = v_line[0]
                x_v = (x1_v + x2_v) / 2
                if 0 <= x_v < image_shape[1] and 0 <= y_h < image_shape[0]:
                    intersections.append({
                        'x': float(x_v),
                        'y': float(y_h),
                        'horizontal_line': h_line[0],
                        'vertical_line': v_line[0]
                    })
        return intersections
    
    def estimate_transformation(self, grid_data: Dict) -> Dict:
        """
        Fit 4th degree polynomials to horizontal and vertical lines.
        """
        horizontal_lines = grid_data.get('horizontal_lines', [])
        vertical_lines = grid_data.get('vertical_lines', [])
        intersections = grid_data.get('intersections', [])
        
        # Group points by line
        horizontal_polynomials = []
        vertical_polynomials = []
        
        # Fit polynomials to horizontal lines
        for h_line in horizontal_lines:
            x1, y1, x2, y2 = h_line[0]
            # Collect points along this line
            y = (y1 + y2) / 2
            x_points = np.linspace(min(x1, x2), max(x1, x2), 100)
            y_points = np.full_like(x_points, y)
            
            # Fit 4th degree polynomial: y = a + bx + cx² + dx³ + ex⁴
            try:
                coeffs = np.polyfit(x_points, y_points, self.polynomial_degree)
                horizontal_polynomials.append({
                    'coefficients': coeffs.tolist(),
                    'y_mean': float(y)
                })
            except:
                pass
        
        # Fit polynomials to vertical lines
        for v_line in vertical_lines:
            x1, y1, x2, y2 = v_line[0]
            x = (x1 + x2) / 2
            y_points = np.linspace(min(y1, y2), max(y1, y2), 100)
            x_points = np.full_like(y_points, x)
            
            try:
                coeffs = np.polyfit(y_points, x_points, self.polynomial_degree)
                vertical_polynomials.append({
                    'coefficients': coeffs.tolist(),
                    'x_mean': float(x)
                })
            except:
                pass
        
        return {
            'horizontal_polynomials': horizontal_polynomials,
            'vertical_polynomials': vertical_polynomials,
            'degree': self.polynomial_degree,
            'intersection_count': len(intersections)
        }
    
    def apply_transformation(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """
        Apply polynomial transformation using forward mapping.
        """
        h, w = image.shape[:2]
        transformed = np.zeros_like(image)
        
        # Create mapping from original to transformed coordinates
        # This is simplified - full implementation would use inverse mapping
        # For now, return original (full implementation needed)
        
        # TODO: Implement full polynomial warp
        # This requires:
        # 1. Create dense mapping grid
        # 2. Apply polynomial transformations
        # 3. Use interpolation to fill output
        
        return image  # Placeholder
    
    def calculate_quality(self, original_grid: Dict, transformed_grid: Dict) -> Dict:
        """Calculate quality metrics."""
        # Similar to barrel transformer
        orig_intersections = original_grid.get('intersections', [])
        trans_intersections = transformed_grid.get('intersections', [])
        
        if len(orig_intersections) == 0 or len(trans_intersections) == 0:
            return {
                'r2': 0.0,
                'rmse': float('inf'),
                'mae': float('inf'),
                'max_error': float('inf'),
                'quality': 'poor'
            }
        
        min_count = min(len(orig_intersections), len(trans_intersections))
        errors = []
        
        for i in range(min_count):
            orig = orig_intersections[i]
            trans = trans_intersections[i]
            error = np.sqrt((orig['x'] - trans['x'])**2 + (orig['y'] - trans['y'])**2)
            errors.append(error)
        
        if len(errors) == 0:
            return {
                'r2': 0.0,
                'rmse': float('inf'),
                'mae': float('inf'),
                'max_error': float('inf'),
                'quality': 'poor'
            }
        
        errors = np.array(errors)
        rmse = np.sqrt(np.mean(errors**2))
        mae = np.mean(np.abs(errors))
        max_error = np.max(errors)
        
        mean_error = np.mean(errors)
        ss_res = np.sum((errors - mean_error)**2)
        ss_tot = np.sum(errors**2) if len(errors) > 0 else 1
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        r2 = max(0, min(1, r2))
        
        if r2 > 0.95 and rmse < 2:
            quality = 'excellent'
        elif r2 > 0.90 and rmse < 5:
            quality = 'good'
        elif r2 > 0.85 and rmse < 10:
            quality = 'fair'
        else:
            quality = 'poor'
        
        return {
            'r2': float(r2),
            'rmse': float(rmse),
            'mae': float(mae),
            'max_error': float(max_error),
            'quality': quality,
            'intersection_count': min_count
        }
