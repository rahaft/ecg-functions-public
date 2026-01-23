"""
Visualizer Module
Matplotlib routines for visualizing edge detection results
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
import cv2


class Visualizer:
    """
    Visualization utilities for edge detection benchmarking.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (16, 12)):
        """
        Initialize Visualizer.
        
        Args:
            figsize: Figure size (width, height) in inches
        """
        self.figsize = figsize
    
    def plot_comparison_grid(self, original: np.ndarray,
                           canny_result: Dict,
                           sobel_result: Dict,
                           laplacian_result: Dict,
                           title: str = "Edge Detection Comparison") -> plt.Figure:
        """
        Generate a 2x2 grid showing Original vs. 3 Edge results.
        
        Args:
            original: Original image
            canny_result: Canny edge detection result (dict with 'edges')
            sobel_result: Sobel edge detection result (dict with 'edges')
            laplacian_result: Laplacian edge detection result (dict with 'edges')
            title: Overall figure title
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Original image
        ax = axes[0, 0]
        if len(original.shape) == 3:
            ax.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        else:
            ax.imshow(original, cmap='gray')
        ax.set_title('Original Image', fontsize=12, fontweight='bold')
        ax.axis('off')
        
        # Canny
        ax = axes[0, 1]
        canny_edges = canny_result.get('edges', np.zeros_like(original))
        ax.imshow(canny_edges, cmap='gray')
        ax.set_title('Canny Edge Detection', fontsize=12, fontweight='bold')
        ax.axis('off')
        
        # Sobel
        ax = axes[1, 0]
        sobel_edges = sobel_result.get('edges', np.zeros_like(original))
        ax.imshow(sobel_edges, cmap='gray')
        ax.set_title('Sobel Edge Detection', fontsize=12, fontweight='bold')
        ax.axis('off')
        
        # Laplacian
        ax = axes[1, 1]
        laplacian_edges = laplacian_result.get('edges', np.zeros_like(original))
        ax.imshow(laplacian_edges, cmap='gray')
        ax.set_title('Laplacian Edge Detection', fontsize=12, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    def plot_document_extraction(self, original: np.ndarray,
                                edge_map: np.ndarray,
                                corners: List[List[int]],
                                method: str = "Edge Detection") -> plt.Figure:
        """
        Visualize document boundary extraction.
        
        Args:
            original: Original image
            edge_map: Edge detection result
            corners: 4 corner points
            method: Method name for title
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle(f'Document Boundary Extraction - {method}', fontsize=14, fontweight='bold')
        
        # Original with corners
        ax = axes[0]
        if len(original.shape) == 3:
            display = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        else:
            display = original
        ax.imshow(display)
        
        if corners:
            corners_array = np.array(corners, dtype=np.int32)
            # Draw rectangle
            corners_closed = np.vstack([corners_array, corners_array[0]])
            ax.plot(corners_closed[:, 0], corners_closed[:, 1], 'r-', linewidth=3, label='Document Boundary')
            # Draw corner points
            ax.scatter(corners_array[:, 0], corners_array[:, 1], c='red', s=100, marker='o', zorder=5)
            ax.legend()
        
        ax.set_title('Original with Document Boundary', fontsize=12)
        ax.axis('off')
        
        # Edge map
        ax = axes[1]
        ax.imshow(edge_map, cmap='gray')
        ax.set_title('Edge Detection Result', fontsize=12)
        ax.axis('off')
        
        plt.tight_layout()
        return fig
    
    def plot_ecg_signal_extraction(self, original: np.ndarray,
                                  edge_map: np.ndarray,
                                  skeletonized: np.ndarray,
                                  coordinates: List[Tuple[int, int]],
                                  method: str = "Edge Detection") -> plt.Figure:
        """
        Visualize ECG signal extraction.
        
        Args:
            original: Original image
            edge_map: Edge detection result
            skeletonized: Skeletonized edge map
            coordinates: Extracted (x, y) coordinates
            method: Method name for title
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'ECG Signal Extraction - {method}', fontsize=14, fontweight='bold')
        
        # Original
        ax = axes[0, 0]
        if len(original.shape) == 3:
            ax.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        else:
            ax.imshow(original, cmap='gray')
        ax.set_title('Original Image', fontsize=11)
        ax.axis('off')
        
        # Edge map
        ax = axes[0, 1]
        ax.imshow(edge_map, cmap='gray')
        ax.set_title(f'Edge Detection ({len(coordinates)} points)', fontsize=11)
        ax.axis('off')
        
        # Skeletonized
        ax = axes[1, 0]
        ax.imshow(skeletonized, cmap='gray')
        ax.set_title('Skeletonized (1-pixel wide)', fontsize=11)
        ax.axis('off')
        
        # Signal plot (if coordinates available)
        ax = axes[1, 1]
        if coordinates and len(coordinates) > 0:
            x_coords = [c[0] for c in coordinates]
            y_coords = [c[1] for c in coordinates]
            # Sort by x for plotting
            sorted_indices = np.argsort(x_coords)
            x_sorted = np.array(x_coords)[sorted_indices]
            y_sorted = np.array(y_coords)[sorted_indices]
            
            ax.plot(x_sorted, -y_sorted, 'b-', linewidth=0.5, alpha=0.7)
            ax.set_title(f'Extracted Signal ({len(coordinates)} points)', fontsize=11)
            ax.set_xlabel('X (Time)')
            ax.set_ylabel('Y (Voltage)')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No coordinates extracted', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Signal Plot', fontsize=11)
        
        plt.tight_layout()
        return fig
    
    def save_figure(self, fig: plt.Figure, filepath: str, dpi: int = 150) -> None:
        """
        Save figure to file.
        
        Args:
            fig: Matplotlib figure
            filepath: Output file path
            dpi: Resolution (dots per inch)
        """
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
