"""
ExtractionEngine Module
Specialized extraction functions for document boundaries and ECG signal
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
try:
    from skimage.morphology import skeletonize
    from skimage import img_as_bool
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("Warning: scikit-image not available. Skeletonization will use fallback method.")


class ExtractionEngine:
    """
    Extraction engine for document boundaries and ECG signal digitization.
    """
    
    def __init__(self):
        """Initialize ExtractionEngine."""
        pass
    
    def find_document(self, edge_map: np.ndarray,
                     min_area_ratio: float = 0.1) -> Dict[str, any]:
        """
        Find document boundaries using the edge map.
        Looks for the largest 4-vertex contour (rectangular document).
        
        Args:
            edge_map: Binary edge map
            min_area_ratio: Minimum area ratio (relative to image size) for valid document
            
        Returns:
            Dictionary with:
            - 'corners': 4 corner points [[x1, y1], [x2, y2], ...]
            - 'contour': Largest rectangular contour
            - 'area': Contour area
            - 'found': Boolean indicating if document was found
        """
        # Find contours
        contours, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return {
                'corners': None,
                'contour': None,
                'area': 0,
                'found': False
            }
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Find the largest rectangular contour
        image_area = edge_map.shape[0] * edge_map.shape[1]
        min_area = image_area * min_area_ratio
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's a 4-vertex rectangle
            if len(approx) == 4:
                # Get corner points
                corners = approx.reshape(4, 2).tolist()
                
                return {
                    'corners': corners,
                    'contour': contour,
                    'area': int(area),
                    'found': True
                }
        
        # If no 4-vertex contour found, return largest contour
        largest_contour = contours[0]
        area = cv2.contourArea(largest_contour)
        
        # Approximate to get corners
        epsilon = 0.02 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)
        
        if len(approx) >= 4:
            # Take first 4 points
            corners = approx[:4].reshape(4, 2).tolist()
        else:
            # Get bounding rectangle corners
            x, y, w, h = cv2.boundingRect(largest_contour)
            corners = [
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h]
            ]
        
        return {
            'corners': corners,
            'contour': largest_contour,
            'area': int(area),
            'found': len(approx) == 4
        }
    
    def digitize_signal(self, edge_map: np.ndarray,
                       apply_skeletonization: bool = True) -> Dict[str, any]:
        """
        Extract (x, y) coordinates from edge map representing ECG signal.
        
        Args:
            edge_map: Binary edge map
            apply_skeletonization: Whether to apply skeletonization for 1-pixel-wide lines
            
        Returns:
            Dictionary with:
            - 'coordinates': List of (x, y) tuples
            - 'skeletonized': Skeletonized image (if applied)
            - 'num_points': Number of extracted points
        """
        if apply_skeletonization and SKIMAGE_AVAILABLE:
            # Convert to boolean for skeletonization
            binary = img_as_bool(edge_map > 0)
            skeleton = skeletonize(binary)
            skeleton_uint8 = (skeleton.astype(np.uint8) * 255)
        else:
            # Fallback: use original edge map
            skeleton_uint8 = edge_map.copy()
            if apply_skeletonization:
                # Simple thinning using morphological operations
                kernel = np.ones((3, 3), np.uint8)
                skeleton_uint8 = cv2.morphologyEx(edge_map, cv2.MORPH_OPEN, kernel)
        
        # Extract coordinates where edge pixels exist
        y_coords, x_coords = np.where(skeleton_uint8 > 0)
        coordinates = list(zip(x_coords.tolist(), y_coords.tolist()))
        
        return {
            'coordinates': coordinates,
            'skeletonized': skeleton_uint8,
            'num_points': len(coordinates)
        }
    
    def apply_tps_correction(self, points: List[Tuple[float, float]],
                            source_points: List[Tuple[float, float]],
                            target_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Apply Thin Plate Spline (TPS) correction for geometric distortion.
        
        Args:
            points: List of (x, y) points to transform
            source_points: Source control points (4 corners)
            target_points: Target control points (corrected corners)
            
        Returns:
            List of corrected (x, y) points
        """
        try:
            from scipy.spatial.distance import cdist
            from scipy.linalg import solve
            
            # Convert to numpy arrays
            points = np.array(points)
            source = np.array(source_points)
            target = np.array(target_points)
            
            if len(source) != len(target) or len(source) < 3:
                return points.tolist()
            
            # TPS transformation
            n = len(source)
            
            # Build TPS matrix
            K = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    r = np.linalg.norm(source[i] - source[j])
                    if r > 0:
                        K[i, j] = r**2 * np.log(r)
            
            # Build system matrix
            P = np.hstack([np.ones((n, 1)), source])
            L = np.vstack([
                np.hstack([K, P]),
                np.hstack([P.T, np.zeros((3, 3))])
            ])
            
            # Solve for transformation parameters
            Y = np.vstack([target, np.zeros((3, 2))])
            W = solve(L, Y)
            
            # Apply transformation to points
            corrected = []
            for point in points:
                # Calculate TPS transformation
                u = np.zeros(2)
                for i in range(n):
                    r = np.linalg.norm(point - source[i])
                    if r > 0:
                        u += W[i] * (r**2 * np.log(r))
                u += W[n] + W[n+1] * point[0] + W[n+2] * point[1]
                corrected.append(tuple(u))
            
            return corrected
        except ImportError:
            # Fallback: Use affine transformation
            return self.apply_affine_correction(points, source_points, target_points)
    
    def apply_affine_correction(self, points: List[Tuple[float, float]],
                               source_points: List[Tuple[float, float]],
                               target_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Apply Affine transformation for geometric correction.
        
        Args:
            points: List of (x, y) points to transform
            source_points: Source control points (minimum 3)
            target_points: Target control points (minimum 3)
            
        Returns:
            List of corrected (x, y) points
        """
        if len(source_points) < 3 or len(target_points) < 3:
            return points
        
        # Use first 3 points for affine transformation
        src = np.array(source_points[:3], dtype=np.float32)
        dst = np.array(target_points[:3], dtype=np.float32)
        
        # Calculate affine transformation matrix
        M = cv2.getAffineTransform(src, dst)
        
        # Apply transformation to all points
        points_array = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
        corrected_array = cv2.transform(points_array, M)
        corrected = [tuple(p[0]) for p in corrected_array]
        
        return corrected
