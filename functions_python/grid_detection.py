"""
Enhanced Grid Detection Module
Implements polynomial line fitting for ECG grid lines with oscillation detection
"""

import numpy as np
import cv2
from scipy import signal
from scipy.optimize import curve_fit
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Tuple, Optional
import warnings


class GridDetector:
    """Enhanced grid detection with polynomial line fitting"""
    
    def __init__(self, max_polynomial_degree: int = 3):
        """
        Initialize grid detector
        
        Args:
            max_polynomial_degree: Maximum polynomial degree to use (1=linear, 2=quadratic, 3=cubic)
        """
        self.max_polynomial_degree = max_polynomial_degree
        self.grid_spacing_mm = 1.0  # mm per small square
        
    def detect_grid(self, image: np.ndarray) -> Dict:
        """
        Detect ECG grid lines using Hough Transform and polynomial fitting
        
        Args:
            image: Preprocessed binary image
            
        Returns:
            Dictionary containing detected lines, equations, and intersections
        """
        # Detect horizontal and vertical lines using Hough Transform
        horizontal_lines_raw, vertical_lines_raw = self._detect_lines_hough(image)
        
        # Fit polynomial equations to detected lines
        horizontal_lines = self._fit_polynomial_lines(horizontal_lines_raw, 'horizontal', image.shape)
        vertical_lines = self._fit_polynomial_lines(vertical_lines_raw, 'vertical', image.shape)
        
        # Validate lines for oscillation
        horizontal_lines = self._validate_oscillation(horizontal_lines, 'horizontal', image.shape)
        vertical_lines = self._validate_oscillation(vertical_lines, 'vertical', image.shape)
        
        # Find grid intersections
        intersections = self._find_grid_intersections(horizontal_lines, vertical_lines, image.shape)
        
        # Calculate grid spacing
        h_spacing = self._calculate_grid_spacing(horizontal_lines, image.shape[0])
        v_spacing = self._calculate_grid_spacing(vertical_lines, image.shape[1])
        
        return {
            'horizontal_lines': horizontal_lines,
            'vertical_lines': vertical_lines,
            'intersections': intersections,
            'horizontal_spacing': h_spacing,
            'vertical_spacing': v_spacing,
            'image_shape': image.shape
        }
    
    def _detect_lines_hough(self, image: np.ndarray) -> Tuple[List, List]:
        """Detect lines using Hough Transform"""
        # Use Canny edge detection
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Detect horizontal lines (theta near 0 or pi)
        horizontal_lines = []
        vertical_lines = []
        
        # Use Probabilistic Hough Transform for better performance
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, 
                                minLineLength=50, maxLineGap=10)
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Calculate angle
                dx = x2 - x1
                dy = y2 - y1
                angle = np.arctan2(abs(dy), abs(dx)) * 180 / np.pi
                
                # Classify as horizontal or vertical
                if angle < 15 or angle > 165:  # Horizontal (within 15 degrees)
                    horizontal_lines.append((x1, y1, x2, y2))
                elif 75 < angle < 105:  # Vertical (within 15 degrees)
                    vertical_lines.append((x1, y1, x2, y2))
        
        return horizontal_lines, vertical_lines
    
    def _fit_polynomial_lines(self, raw_lines: List[Tuple], orientation: str, 
                             image_shape: Tuple[int, int]) -> List[Dict]:
        """
        Fit polynomial equations to detected lines
        
        Args:
            raw_lines: List of (x1, y1, x2, y2) line segments
            orientation: 'horizontal' or 'vertical'
            image_shape: (height, width) of image
            
        Returns:
            List of dictionaries with line equations and metadata
        """
        if not raw_lines:
            return []
        
        # Cluster lines that are close together
        clustered_lines = self._cluster_lines(raw_lines, orientation, image_shape)
        
        fitted_lines = []
        for cluster in clustered_lines:
            # Extract points from all line segments in cluster
            points = []
            for line in cluster:
                x1, y1, x2, y2 = line
                # Sample points along the line
                num_points = max(10, int(np.sqrt((x2-x1)**2 + (y2-y1)**2) / 5))
                for i in range(num_points + 1):
                    t = i / num_points
                    x = x1 + t * (x2 - x1)
                    y = y1 + t * (y2 - y1)
                    points.append((x, y))
            
            if len(points) < 3:
                continue
            
            points = np.array(points)
            
            # Fit polynomial of appropriate degree
            line_data = self._fit_polynomial(points, orientation, image_shape)
            if line_data:
                fitted_lines.append(line_data)
        
        return fitted_lines
    
    def _cluster_lines(self, lines: List[Tuple], orientation: str, 
                      image_shape: Tuple[int, int]) -> List[List[Tuple]]:
        """Cluster lines that are close together"""
        if not lines:
            return []
        
        # Calculate representative position for each line
        positions = []
        for line in lines:
            x1, y1, x2, y2 = line
            if orientation == 'horizontal':
                # Use average y-coordinate
                pos = (y1 + y2) / 2
            else:
                # Use average x-coordinate
                pos = (x1 + x2) / 2
            positions.append((pos, line))
        
        # Sort by position
        positions.sort(key=lambda x: x[0])
        
        # Cluster lines within threshold distance
        threshold = 10  # pixels
        clusters = []
        current_cluster = [positions[0][1]]
        current_pos = positions[0][0]
        
        for pos, line in positions[1:]:
            if abs(pos - current_pos) < threshold:
                current_cluster.append(line)
            else:
                clusters.append(current_cluster)
                current_cluster = [line]
                current_pos = pos
        
        if current_cluster:
            clusters.append(current_cluster)
        
        return clusters
    
    def _fit_polynomial(self, points: np.ndarray, orientation: str, 
                      image_shape: Tuple[int, int]) -> Optional[Dict]:
        """
        Fit polynomial to points with adaptive degree selection
        
        Args:
            points: Array of (x, y) points
            orientation: 'horizontal' or 'vertical'
            image_shape: (height, width) of image
            
        Returns:
            Dictionary with polynomial coefficients and metadata
        """
        if len(points) < 2:
            return None
        
        # Sort points by x or y coordinate
        if orientation == 'horizontal':
            # For horizontal lines: y = f(x)
            points = points[points[:, 0].argsort()]
            x = points[:, 0]
            y = points[:, 1]
            domain_size = image_shape[1]
        else:
            # For vertical lines: x = f(y)
            points = points[points[:, 1].argsort()]
            x = points[:, 1]
            y = points[:, 0]
            domain_size = image_shape[0]
        
        # Try different polynomial degrees and select best
        best_degree = 1
        best_r2 = -np.inf
        best_coeffs = None
        
        for degree in range(1, min(self.max_polynomial_degree + 1, len(points))):
            try:
                coeffs = np.polyfit(x, y, degree)
                poly_func = np.poly1d(coeffs)
                y_pred = poly_func(x)
                
                # Calculate R-squared
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - np.mean(y)) ** 2)
                if ss_tot > 0:
                    r2 = 1 - (ss_res / ss_tot)
                else:
                    r2 = 0
                
                # Prefer lower degree if R2 is similar (within 0.01)
                if r2 > best_r2 + 0.01 or (r2 > best_r2 - 0.01 and degree < best_degree):
                    best_degree = degree
                    best_r2 = r2
                    best_coeffs = coeffs
            except:
                continue
        
        if best_coeffs is None:
            return None
        
        # Create polynomial function
        poly_func = np.poly1d(best_coeffs)
        
        return {
            'coefficients': best_coeffs.tolist(),
            'degree': best_degree,
            'r_squared': float(best_r2),
            'orientation': orientation,
            'domain': (float(x.min()), float(x.max())),
            'range': (float(y.min()), float(y.max())),
            'function': poly_func
        }
    
    def _validate_oscillation(self, lines: List[Dict], orientation: str, 
                             image_shape: Tuple[int, int]) -> List[Dict]:
        """
        Validate that higher-order lines don't oscillate away from reference
        
        Args:
            lines: List of line dictionaries
            orientation: 'horizontal' or 'vertical'
            image_shape: (height, width) of image
            
        Returns:
            Filtered list of valid lines
        """
        if orientation == 'horizontal':
            # For horizontal lines, check they don't oscillate vertically
            # Compare with linear fit
            valid_lines = []
            for line in lines:
                if line['degree'] == 1:
                    valid_lines.append(line)
                else:
                    # Check oscillation by comparing with linear fit
                    x_min, x_max = line['domain']
                    x_test = np.linspace(x_min, x_max, 100)
                    y_poly = line['function'](x_test)
                    
                    # Fit linear to same points
                    y_linear = np.polyval(np.polyfit(x_test, y_poly, 1), x_test)
                    
                    # Check maximum deviation
                    max_deviation = np.max(np.abs(y_poly - y_linear))
                    
                    # Allow small deviation (5 pixels)
                    if max_deviation < 5:
                        valid_lines.append(line)
                    else:
                        # Replace with linear fit
                        coeffs_linear = np.polyfit(x_test, y_poly, 1)
                        line['coefficients'] = coeffs_linear.tolist()
                        line['degree'] = 1
                        line['function'] = np.poly1d(coeffs_linear)
                        valid_lines.append(line)
        else:
            # For vertical lines, check they don't oscillate horizontally
            valid_lines = []
            for line in lines:
                if line['degree'] == 1:
                    valid_lines.append(line)
                else:
                    y_min, y_max = line['domain']
                    y_test = np.linspace(y_min, y_max, 100)
                    x_poly = line['function'](y_test)
                    
                    # Fit linear to same points
                    x_linear = np.polyval(np.polyfit(y_test, x_poly, 1), y_test)
                    
                    # Check maximum deviation
                    max_deviation = np.max(np.abs(x_poly - x_linear))
                    
                    # Allow small deviation (5 pixels)
                    if max_deviation < 5:
                        valid_lines.append(line)
                    else:
                        # Replace with linear fit
                        coeffs_linear = np.polyfit(y_test, x_poly, 1)
                        line['coefficients'] = coeffs_linear.tolist()
                        line['degree'] = 1
                        line['function'] = np.poly1d(coeffs_linear)
                        valid_lines.append(line)
        
        return valid_lines
    
    def _find_grid_intersections(self, horizontal_lines: List[Dict], 
                                 vertical_lines: List[Dict],
                                 image_shape: Tuple[int, int]) -> List[Dict]:
        """
        Find intersections between horizontal and vertical grid lines
        
        Args:
            horizontal_lines: List of horizontal line dictionaries
            vertical_lines: List of vertical line dictionaries
            image_shape: (height, width) of image
            
        Returns:
            List of intersection points
        """
        intersections = []
        
        for h_line in horizontal_lines:
            for v_line in vertical_lines:
                intersection = self._solve_intersection(h_line, v_line, image_shape)
                if intersection:
                    intersections.append(intersection)
        
        return intersections
    
    def _solve_intersection(self, h_line: Dict, v_line: Dict, 
                           image_shape: Tuple[int, int]) -> Optional[Dict]:
        """
        Solve intersection between horizontal and vertical polynomial lines
        
        For horizontal: y = f_h(x)
        For vertical: x = f_v(y)
        
        Solve: x = f_v(f_h(x))
        """
        try:
            h_func = h_line['function']
            v_func = v_line['function']
            
            # Get overlapping domain
            h_x_min, h_x_max = h_line['domain']
            v_y_min, v_y_max = v_line['domain']
            
            # Sample points to find intersection
            x_samples = np.linspace(h_x_min, h_x_max, 100)
            y_samples = h_func(x_samples)
            
            # Find where vertical line intersects
            valid_indices = (y_samples >= v_y_min) & (y_samples <= v_y_max)
            if not np.any(valid_indices):
                return None
            
            x_valid = x_samples[valid_indices]
            y_valid = y_samples[valid_indices]
            
            # Calculate x from vertical line
            x_from_v = v_func(y_valid)
            
            # Find where x matches
            differences = np.abs(x_valid - x_from_v)
            min_idx = np.argmin(differences)
            
            if differences[min_idx] < 5:  # Within 5 pixels
                x_int = x_valid[min_idx]
                y_int = y_valid[min_idx]
                
                # Ensure within image bounds
                if 0 <= x_int < image_shape[1] and 0 <= y_int < image_shape[0]:
                    return {
                        'x': float(x_int),
                        'y': float(y_int)
                    }
        except Exception as e:
            warnings.warn(f"Error solving intersection: {e}")
            return None
        
        return None
    
    def _calculate_grid_spacing(self, lines: List[Dict], dimension_size: int) -> float:
        """Calculate average grid spacing from detected lines"""
        if len(lines) < 2:
            return 10.0  # Default spacing
        
        # Extract representative positions
        positions = []
        for line in lines:
            if line['orientation'] == 'horizontal':
                # Use y-value at middle of domain
                x_mid = (line['domain'][0] + line['domain'][1]) / 2
                y_mid = line['function'](x_mid)
                positions.append(y_mid)
            else:
                # Use x-value at middle of domain
                y_mid = (line['domain'][0] + line['domain'][1]) / 2
                x_mid = line['function'](y_mid)
                positions.append(x_mid)
        
        positions = sorted(positions)
        
        # Calculate spacings
        spacings = np.diff(positions)
        
        # Filter out outliers (spacings that are too different)
        if len(spacings) > 0:
            median_spacing = np.median(spacings)
            valid_spacings = spacings[np.abs(spacings - median_spacing) < median_spacing * 0.5]
            
            if len(valid_spacings) > 0:
                return float(np.median(valid_spacings))
        
        return 10.0  # Default spacing
