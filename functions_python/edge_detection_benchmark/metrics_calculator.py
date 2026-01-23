"""
MetricsCalculator Module
Computes quantitative metrics for edge detection comparison
"""

import numpy as np
import cv2
from typing import Dict, List


class MetricsCalculator:
    """
    Calculate metrics for edge detection evaluation.
    """
    
    @staticmethod
    def calculate_edge_density(edge_map: np.ndarray) -> float:
        """
        Calculate edge pixel density (percentage of active pixels).
        
        Args:
            edge_map: Binary edge map (0 = background, 255 = edge)
            
        Returns:
            Edge density as percentage (0-100)
        """
        total_pixels = edge_map.size
        edge_pixels = np.sum(edge_map > 0)
        density = (edge_pixels / total_pixels) * 100.0
        return float(density)
    
    @staticmethod
    def calculate_connectivity_score(edge_map: np.ndarray) -> Dict[str, int]:
        """
        Calculate connectivity score (number of continuous contours).
        
        Args:
            edge_map: Binary edge map
            
        Returns:
            Dictionary with:
            - 'num_contours': Number of detected contours
            - 'largest_contour_area': Area of largest contour
            - 'total_contour_area': Total area of all contours
        """
        # Find contours
        contours, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return {
                'num_contours': 0,
                'largest_contour_area': 0,
                'total_contour_area': 0
            }
        
        # Calculate areas
        areas = [cv2.contourArea(contour) for contour in contours]
        largest_area = max(areas) if areas else 0
        total_area = sum(areas)
        
        return {
            'num_contours': len(contours),
            'largest_contour_area': int(largest_area),
            'total_contour_area': int(total_area)
        }
    
    @staticmethod
    def calculate_salt_pepper_noise(edge_map: np.ndarray) -> float:
        """
        Estimate salt and pepper noise (isolated edge pixels).
        
        Args:
            edge_map: Binary edge map
            
        Returns:
            Noise score (lower is better, 0-100)
        """
        # Use morphological operations to find isolated pixels
        kernel = np.ones((3, 3), np.uint8)
        
        # Erode to find isolated pixels
        eroded = cv2.erode(edge_map, kernel, iterations=1)
        
        # Find pixels that disappear after erosion (isolated)
        isolated = cv2.subtract(edge_map, eroded)
        isolated_pixels = np.sum(isolated > 0)
        
        total_edge_pixels = np.sum(edge_map > 0)
        
        if total_edge_pixels == 0:
            return 0.0
        
        noise_ratio = (isolated_pixels / total_edge_pixels) * 100.0
        return float(noise_ratio)
    
    @staticmethod
    def calculate_line_continuity(edge_map: np.ndarray) -> float:
        """
        Calculate line continuity score (higher = more continuous lines).
        
        Args:
            edge_map: Binary edge map
            
        Returns:
            Continuity score (0-100, higher is better)
        """
        # Use skeletonization to find continuous lines
        try:
            from skimage.morphology import skeletonize
            from skimage import img_as_bool
            
            # Convert to boolean for skeletonization
            binary = img_as_bool(edge_map > 0)
            skeleton = skeletonize(binary)
            
            # Count connected components in skeleton
            num_labels, labels = cv2.connectedComponents(skeleton.astype(np.uint8) * 255)
            
            # Calculate average component size
            if num_labels > 1:
                component_sizes = [np.sum(labels == i) for i in range(1, num_labels)]
                avg_size = np.mean(component_sizes)
                total_pixels = skeleton.size
                continuity = (avg_size / total_pixels) * 100.0 if total_pixels > 0 else 0.0
            else:
                continuity = 0.0
            
            return float(continuity)
        except ImportError:
            # Fallback if skimage not available
            # Use contour-based continuity
            contours, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) == 0:
                return 0.0
            
            # Calculate average contour length
            lengths = [len(contour) for contour in contours]
            avg_length = np.mean(lengths)
            max_length = max(lengths) if lengths else 0
            
            # Continuity = ratio of average to max (higher = more continuous)
            continuity = (avg_length / max_length * 100.0) if max_length > 0 else 0.0
            return float(continuity)
    
    def calculate_all_metrics(self, edge_map: np.ndarray) -> Dict[str, float]:
        """
        Calculate all metrics for an edge map.
        
        Args:
            edge_map: Binary edge map
            
        Returns:
            Dictionary with all calculated metrics
        """
        return {
            'edge_density': self.calculate_edge_density(edge_map),
            'connectivity': self.calculate_connectivity_score(edge_map),
            'salt_pepper_noise': self.calculate_salt_pepper_noise(edge_map),
            'line_continuity': self.calculate_line_continuity(edge_map)
        }
    
    def compare_methods(self, results: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Compare multiple edge detection methods.
        
        Args:
            results: Dictionary with method names as keys and edge detection results as values
                   Each result should have 'edges' key with edge map
                   
        Returns:
            Dictionary with metrics for each method
        """
        comparison = {}
        
        for method_name, result in results.items():
            edge_map = result.get('edges')
            if edge_map is not None:
                comparison[method_name] = self.calculate_all_metrics(edge_map)
        
        return comparison
    
    def print_comparison_table(self, comparison: Dict[str, Dict]) -> None:
        """
        Print a formatted comparison table.
        
        Args:
            comparison: Dictionary with metrics for each method
        """
        print("\n" + "="*80)
        print("EDGE DETECTION METHOD COMPARISON")
        print("="*80)
        
        # Header
        print(f"{'Method':<15} {'Density %':<12} {'Contours':<10} {'Noise %':<12} {'Continuity %':<15}")
        print("-"*80)
        
        # Data rows
        for method_name, metrics in comparison.items():
            density = metrics.get('edge_density', 0)
            connectivity = metrics.get('connectivity', {})
            num_contours = connectivity.get('num_contours', 0)
            noise = metrics.get('salt_pepper_noise', 0)
            continuity = metrics.get('line_continuity', 0)
            
            print(f"{method_name:<15} {density:<12.2f} {num_contours:<10} {noise:<12.2f} {continuity:<15.2f}")
        
        print("="*80)
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        
        # Best for document boundaries (low noise, good contours)
        best_doc = min(comparison.items(), 
                      key=lambda x: x[1].get('salt_pepper_noise', 100))
        print(f"  Document Boundaries: {best_doc[0]} (lowest noise: {best_doc[1].get('salt_pepper_noise', 0):.2f}%)")
        
        # Best for ECG signal (high continuity)
        best_ecg = max(comparison.items(), 
                      key=lambda x: x[1].get('line_continuity', 0))
        print(f"  ECG Signal Extraction: {best_ecg[0]} (highest continuity: {best_ecg[1].get('line_continuity', 0):.2f}%)")
        
        print()
