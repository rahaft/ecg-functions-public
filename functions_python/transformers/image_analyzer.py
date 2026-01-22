"""
Comprehensive Image Analysis Module
Detects image type, contrast, smudges, and calculates metrics
"""

import numpy as np
import cv2
from typing import Dict
from scipy.spatial.distance import cdist


class ImageAnalyzer:
    """Analyze ECG images for type, contrast, smudges, and quality"""
    
    def detect_image_type(self, image: np.ndarray) -> Dict:
        """Detect if image is B&W or Red/Black/White"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect red
        red_lower1 = np.array([0, 50, 50])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([170, 50, 50])
        red_upper2 = np.array([180, 255, 255])
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_pixels = np.sum(red_mask > 0)
        has_red = red_pixels > (image.shape[0] * image.shape[1] * 0.01)
        
        # Detect black
        black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 50]))
        black_pixels = np.sum(black_mask > 0)
        has_black = black_pixels > (image.shape[0] * image.shape[1] * 0.05)
        
        # Detect white
        white_mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
        white_pixels = np.sum(white_mask > 0)
        has_white = white_pixels > (image.shape[0] * image.shape[1] * 0.1)
        
        # Determine type
        if has_red and has_black and has_white:
            image_type = 'red_black_white'
            confidence = min(1.0, (red_pixels + black_pixels + white_pixels) / (image.shape[0] * image.shape[1] * 0.5))
        else:
            image_type = 'bw'
            confidence = 1.0 - (red_pixels / (image.shape[0] * image.shape[1]))
        
        return {
            'type': image_type,
            'confidence': float(confidence),
            'has_red': bool(has_red),
            'has_black': bool(has_black),
            'has_white': bool(has_white),
            'red_pixel_count': int(red_pixels),
            'black_pixel_count': int(black_pixels),
            'white_pixel_count': int(white_pixels)
        }
    
    def analyze_contrast(self, image: np.ndarray) -> Dict:
        """Analyze contrast and determine if it can be improved"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        current_contrast = float(np.std(gray))
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        enhanced_contrast = float(np.std(enhanced))
        improvement = enhanced_contrast - current_contrast
        can_improve = improvement > 5.0
        
        return {
            'current_contrast': current_contrast,
            'can_improve': can_improve,
            'suggested_method': 'clahe' if can_improve else 'none',
            'improvement_potential': float(improvement),
            'enhanced_contrast': enhanced_contrast
        }
    
    def detect_smudges(self, image: np.ndarray, method: str = 'morphological') -> Dict:
        """Detect smudges using different methods"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        if method == 'morphological':
            _, dark_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
            kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
            vertical_lines = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_v)
            horizontal_lines = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_h)
            grid_mask = cv2.bitwise_or(vertical_lines, horizontal_lines)
            smudge_mask = cv2.subtract(dark_mask, grid_mask)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            smudge_mask = cv2.morphologyEx(smudge_mask, cv2.MORPH_OPEN, kernel)
            smudge_mask = cv2.dilate(smudge_mask, kernel, iterations=2)
        elif method == 'contour':
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            smudge_mask = np.zeros_like(gray)
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 5000:
                    cv2.fillPoly(smudge_mask, [contour], 255)
        else:
            _, smudge_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        
        smudge_pixels = np.sum(smudge_mask > 0)
        total_pixels = image.shape[0] * image.shape[1]
        smudge_area = (smudge_pixels / total_pixels) * 100
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(smudge_mask, connectivity=8)
        smudge_count = num_labels - 1
        smudge_density = (smudge_count / total_pixels) * 1000
        
        if smudge_area < 0.1:
            qualitative = "No smudges"
        elif smudge_area < 1.0:
            qualitative = "Some smudges"
        elif smudge_area < 5.0:
            qualitative = "Many smudges"
        else:
            qualitative = "Heavy smudges"
        
        return {
            'smudge_count': int(smudge_count),
            'smudge_area': float(smudge_area),
            'smudge_density': float(smudge_density),
            'qualitative': qualitative,
            'method': method
        }
    
    def analyze_red_grid(self, red_image: np.ndarray) -> Dict:
        """Analyze red grid: count black dots and calculate nearest neighbor distances"""
        gray = cv2.cvtColor(red_image, cv2.COLOR_BGR2GRAY) if len(red_image.shape) == 3 else red_image
        _, black_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dots = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1 < area < 100:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    dots.append([cx, cy])
        
        black_dot_count = len(dots)
        if black_dot_count < 2:
            return {
                'black_dot_count': black_dot_count,
                'nearest_neighbor_distance': 0.0,
                'nearest_neighbor_value': 0
            }
        
        dots_array = np.array(dots)
        distances = cdist(dots_array, dots_array, metric='euclidean')
        np.fill_diagonal(distances, np.inf)
        nearest_distances = np.min(distances, axis=1)
        average_distance = float(np.mean(nearest_distances))
        nearest_neighbor_value = int(average_distance * 100000)
        
        return {
            'black_dot_count': black_dot_count,
            'nearest_neighbor_distance': float(average_distance),
            'nearest_neighbor_value': nearest_neighbor_value
        }
