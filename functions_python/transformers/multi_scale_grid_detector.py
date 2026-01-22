"""
Multi-Scale Grid Detection Module
Detects both 1mm (small) and 5mm (large) grid lines

Two-Pass Detection:
- Pass 1: Fine Grid (1mm) - Small kernels
- Pass 2: Bold Grid (5mm) - Large kernels
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional


class MultiScaleGridDetector:
    """
    Multi-Scale Grid Detection for ECG Images
    
    Purpose: Detect both 1mm (small) and 5mm (large) grid lines
    """
    
    def __init__(self, fine_kernel_size: Tuple[int, int] = (1, 10), 
                 bold_kernel_size: Tuple[int, int] = (3, 20)):
        """
        Initialize Multi-Scale Grid Detector
        
        Args:
            fine_kernel_size: Kernel size for fine grid (1mm) detection (default: (1, 10))
            bold_kernel_size: Kernel size for bold grid (5mm) detection (default: (3, 20))
        """
        self.fine_kernel_size = fine_kernel_size
        self.bold_kernel_size = bold_kernel_size
    
    def detect(self, image: np.ndarray) -> Dict:
        """
        Detect both fine and bold grid lines
        
        Args:
            image: Input image (grayscale)
            
        Returns:
            Dictionary with detected grid lines
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Pass 1: Fine Grid (1mm) Detection
        fine_grid = self._detect_fine_grid(gray)
        
        # Pass 2: Bold Grid (5mm) Detection
        bold_grid = self._detect_bold_grid(gray)
        
        # Combine results
        combined_grid = self._combine_grids(fine_grid, bold_grid)
        
        # Validate spacing ratio (5mm should be ~5x 1mm)
        validation = self._validate_spacing(fine_grid, bold_grid)
        
        return {
            'fine_grid': fine_grid,
            'bold_grid': bold_grid,
            'combined_grid': combined_grid,
            'validation': validation,
            'image_shape': gray.shape
        }
    
    def _detect_fine_grid(self, image: np.ndarray) -> Dict:
        """
        Detect fine grid (1mm) using small kernels
        
        Args:
            image: Grayscale image
            
        Returns:
            Dictionary with fine grid detection results
        """
        # Small kernels for thin lines
        # Vertical lines: (1, kernel_height)
        # Horizontal lines: (kernel_width, 1)
        v_kernel_size, h_kernel_size = self.fine_kernel_size
        
        # Extract vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_size))
        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
        
        # Extract horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_size, 1))
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Combine
        fine_grid = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0)
        
        # Detect actual line positions using Hough Transform
        edges = cv2.Canny(fine_grid, 50, 150, apertureSize=3)
        
        # Horizontal lines
        h_lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                  minLineLength=image.shape[1]//4, maxLineGap=10)
        
        # Vertical lines (rotate image for vertical detection)
        rotated_edges = cv2.rotate(edges, cv2.ROTATE_90_CLOCKWISE)
        v_lines_rotated = cv2.HoughLinesP(rotated_edges, 1, np.pi/180, threshold=100,
                                          minLineLength=image.shape[0]//4, maxLineGap=10)
        
        # Convert rotated vertical lines back to original coordinates
        v_lines = []
        if v_lines_rotated is not None:
            for line in v_lines_rotated:
                x1, y1, x2, y2 = line[0]
                # Rotate back
                v_lines.append([[y1, image.shape[1] - x1, y2, image.shape[1] - x2]])
        
        return {
            'kernel_size': self.fine_kernel_size,
            'grid_image': fine_grid,
            'horizontal_lines': h_lines.tolist() if h_lines is not None else [],
            'vertical_lines': v_lines if v_lines else [],
            'num_horizontal': len(h_lines) if h_lines is not None else 0,
            'num_vertical': len(v_lines),
            'scale': '1mm'
        }
    
    def _detect_bold_grid(self, image: np.ndarray) -> Dict:
        """
        Detect bold grid (5mm) using large kernels
        
        Args:
            image: Grayscale image
            
        Returns:
            Dictionary with bold grid detection results
        """
        # Large kernels for thick lines
        # Vertical lines: (3, kernel_height)
        # Horizontal lines: (kernel_width, 3)
        v_kernel_size, h_kernel_size = self.bold_kernel_size
        
        # Extract vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, v_kernel_size))
        vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
        
        # Extract horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_size, 3))
        horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
        
        # Combine
        bold_grid = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0)
        
        # Detect actual line positions using Hough Transform
        edges = cv2.Canny(bold_grid, 50, 150, apertureSize=3)
        
        # Horizontal lines
        h_lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                  minLineLength=image.shape[1]//4, maxLineGap=10)
        
        # Vertical lines (rotate image for vertical detection)
        rotated_edges = cv2.rotate(edges, cv2.ROTATE_90_CLOCKWISE)
        v_lines_rotated = cv2.HoughLinesP(rotated_edges, 1, np.pi/180, threshold=100,
                                          minLineLength=image.shape[0]//4, maxLineGap=10)
        
        # Convert rotated vertical lines back to original coordinates
        v_lines = []
        if v_lines_rotated is not None:
            for line in v_lines_rotated:
                x1, y1, x2, y2 = line[0]
                # Rotate back
                v_lines.append([[y1, image.shape[1] - x1, y2, image.shape[1] - x2]])
        
        return {
            'kernel_size': self.bold_kernel_size,
            'grid_image': bold_grid,
            'horizontal_lines': h_lines.tolist() if h_lines is not None else [],
            'vertical_lines': v_lines if v_lines else [],
            'num_horizontal': len(h_lines) if h_lines is not None else 0,
            'num_vertical': len(v_lines),
            'scale': '5mm'
        }
    
    def _combine_grids(self, fine_grid: Dict, bold_grid: Dict) -> Dict:
        """
        Combine fine and bold grid detections
        
        Args:
            fine_grid: Fine grid detection results
            bold_grid: Bold grid detection results
            
        Returns:
            Combined grid results
        """
        # Combine grid images
        combined_image = cv2.addWeighted(fine_grid['grid_image'], 0.5, 
                                        bold_grid['grid_image'], 0.5, 0)
        
        # Combine line lists
        all_horizontal = fine_grid['horizontal_lines'] + bold_grid['horizontal_lines']
        all_vertical = fine_grid['vertical_lines'] + bold_grid['vertical_lines']
        
        return {
            'grid_image': combined_image,
            'horizontal_lines': all_horizontal,
            'vertical_lines': all_vertical,
            'num_horizontal': len(all_horizontal),
            'num_vertical': len(all_vertical),
            'total_lines': len(all_horizontal) + len(all_vertical)
        }
    
    def _validate_spacing(self, fine_grid: Dict, bold_grid: Dict, 
                         tolerance: float = 0.15) -> Dict:
        """
        Validate spacing ratio (5mm should be ~5x 1mm)
        
        Args:
            fine_grid: Fine grid results
            bold_grid: Bold grid results
            tolerance: Allowed deviation from 5:1 ratio (default: 0.15 = 15%)
            
        Returns:
            Validation results
        """
        # Calculate average spacing for each grid type
        # For simplicity, estimate based on number of lines
        
        fine_h_spacing = None
        bold_h_spacing = None
        
        # Estimate spacing from line positions (simplified)
        if fine_grid['num_horizontal'] > 0 and bold_grid['num_horizontal'] > 0:
            # Assume lines are evenly distributed
            # Fine grid should have ~5x more lines than bold grid
            spacing_ratio = fine_grid['num_horizontal'] / max(bold_grid['num_horizontal'], 1)
            
            # Expected ratio is ~5:1 (5mm / 1mm)
            expected_ratio = 5.0
            ratio_valid = abs(spacing_ratio - expected_ratio) / expected_ratio <= tolerance
            
            return {
                'valid': ratio_valid,
                'spacing_ratio': spacing_ratio,
                'expected_ratio': expected_ratio,
                'tolerance': tolerance,
                'message': f'Spacing ratio: {spacing_ratio:.2f} (expected: {expected_ratio:.2f})' if ratio_valid
                          else f'Spacing ratio mismatch: {spacing_ratio:.2f} vs expected {expected_ratio:.2f}'
            }
        
        return {
            'valid': True,
            'spacing_ratio': None,
            'expected_ratio': 5.0,
            'tolerance': tolerance,
            'message': 'Insufficient lines for spacing validation'
        }
