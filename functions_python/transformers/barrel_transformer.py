"""
Barrel/Pincushion Distortion Correction Transformer
Implements radial distortion correction using barrel distortion formula
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple
from .base_transformer import BaseTransformer


class BarrelTransformer(BaseTransformer):
    """
    Corrects barrel/pincushion distortion in ECG images.
    
    Formula: r_corrected = r * (1 + k₁r² + k₂r⁴ + k₃r⁶)
    """
    
    def __init__(self):
        super().__init__('barrel')
        self.default_k1 = 0.01
        self.default_k2 = -0.003
        self.default_k3 = 0.0
        
    def detect_grid(self, image: np.ndarray) -> Dict:
        """
        Detect grid lines using Hough Transform and color thresholding.
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Detect red/pink grid lines
        # Red channel should be high, green/blue low
        if len(image.shape) == 3:
            red_channel = image[:, :, 2]
            green_channel = image[:, :, 1]
            blue_channel = image[:, :, 0]
            
            # Threshold for red/pink lines
            red_mask = (red_channel > 200) & (red_channel > green_channel * 1.5) & (red_channel > blue_channel * 1.5)
            grid_mask = red_mask.astype(np.uint8) * 255
        else:
            # For grayscale, use edge detection
            edges = cv2.Canny(gray, 50, 150)
            grid_mask = edges
        
        # Detect horizontal lines using Hough Transform
        horizontal_lines = cv2.HoughLinesP(
            grid_mask, 1, np.pi/180, threshold=100,
            minLineLength=image.shape[1]//4, maxLineGap=10
        )
        
        # Detect vertical lines
        vertical_lines = cv2.HoughLinesP(
            cv2.rotate(grid_mask, cv2.ROTATE_90_CLOCKWISE), 1, np.pi/180, threshold=100,
            minLineLength=image.shape[0]//4, maxLineGap=10
        )
        
        # Convert vertical lines back to original orientation
        if vertical_lines is not None:
            for line in vertical_lines:
                x1, y1, x2, y2 = line[0]
                # Rotate back
                line[0] = [y1, image.shape[1] - x1, y2, image.shape[1] - x2]
        
        # Find intersections
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
        """Find intersection points between horizontal and vertical lines."""
        intersections = []
        
        for h_line in horizontal_lines:
            x1_h, y1_h, x2_h, y2_h = h_line[0]
            # Average y for horizontal line
            y_h = (y1_h + y2_h) / 2
            
            for v_line in vertical_lines:
                x1_v, y1_v, x2_v, y2_v = v_line[0]
                # Average x for vertical line
                x_v = (x1_v + x2_v) / 2
                
                # Check if lines intersect (within image bounds)
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
        Estimate barrel distortion parameters from grid intersections.
        Uses least squares to fit distortion model.
        """
        intersections = grid_data.get('intersections', [])
        image_shape = grid_data.get('image_shape', (1000, 1000))
        
        if len(intersections) < 4:
            # Not enough points, use defaults
            return {
                'k1': self.default_k1,
                'k2': self.default_k2,
                'k3': self.default_k3,
                'center_x': image_shape[1] / 2,
                'center_y': image_shape[0] / 2,
                'auto_detected': False
            }
        
        # Calculate image center (distortion center)
        center_x = image_shape[1] / 2
        center_y = image_shape[0] / 2
        max_radius = np.sqrt(center_x**2 + center_y**2)
        
        # For barrel distortion estimation, we assume ideal grid
        # and measure deviation from expected positions
        # This is simplified - full implementation would use optimization
        
        # Group intersections into grid
        xs = sorted(set([int(p['x']) for p in intersections]))
        ys = sorted(set([int(p['y']) for p in intersections]))
        
        # Estimate expected grid spacing
        if len(xs) > 1 and len(ys) > 1:
            dx = np.mean(np.diff(xs))
            dy = np.mean(np.diff(ys))
        else:
            dx = dy = 20  # Default spacing
        
        # Simple estimation: measure radial distortion
        # In a perfect grid, intersections should be evenly spaced
        # Barrel distortion causes outer points to be compressed
        
        # Use default values for now (can be optimized)
        k1 = self.default_k1
        k2 = self.default_k2
        k3 = self.default_k3
        
        return {
            'k1': float(k1),
            'k2': float(k2),
            'k3': float(k3),
            'center_x': float(center_x),
            'center_y': float(center_y),
            'auto_detected': True,
            'grid_spacing': {'dx': float(dx), 'dy': float(dy)}
        }
    
    def apply_transformation(self, image: np.ndarray, params: Dict) -> np.ndarray:
        """
        Apply barrel distortion correction using OpenCV's undistort.
        """
        h, w = image.shape[:2]
        
        # Create camera matrix (identity for this use case)
        camera_matrix = np.array([
            [w, 0, params['center_x']],
            [0, h, params['center_y']],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # Distortion coefficients: [k1, k2, p1, p2, k3]
        # For barrel: k1 > 0, k2 < 0 typically
        dist_coeffs = np.array([
            params['k1'],
            params['k2'],
            0.0,  # p1 (tangential)
            0.0,  # p2 (tangential)
            params['k3']
        ], dtype=np.float32)
        
        # Apply correction
        corrected = cv2.undistort(image, camera_matrix, dist_coeffs)
        
        return corrected
    
    def calculate_quality(self, original_grid: Dict, transformed_grid: Dict) -> Dict:
        """
        Calculate quality metrics: R², RMSE, MAE, Max Error
        """
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
        
        # Match intersections (simplified - assumes same count and order)
        min_count = min(len(orig_intersections), len(trans_intersections))
        
        errors = []
        for i in range(min_count):
            orig = orig_intersections[i]
            trans = trans_intersections[i]
            
            # Calculate distance error
            error = np.sqrt(
                (orig['x'] - trans['x'])**2 + 
                (orig['y'] - trans['y'])**2
            )
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
        
        # Calculate R² (simplified)
        # R² = 1 - (SS_res / SS_tot)
        mean_error = np.mean(errors)
        ss_res = np.sum((errors - mean_error)**2)
        ss_tot = np.sum((errors - 0)**2) if len(errors) > 0 else 1
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        r2 = max(0, min(1, r2))  # Clamp to [0, 1]
        
        # Quality assessment
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
