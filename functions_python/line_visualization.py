"""
Line Visualization Module
Visualizes detected grid lines with polynomial equations and checks for oscillation
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Tuple, Optional
import os


class LineVisualizer:
    """Visualize grid lines and validate oscillation"""
    
    def __init__(self, output_dir: str = "data/visualizations"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualization images
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def visualize_grid_lines(self, image: np.ndarray, grid_info: Dict, 
                            filename: Optional[str] = None) -> str:
        """
        Visualize detected grid lines overlaid on original image
        
        Args:
            image: Original ECG image
            grid_info: Grid detection results from GridDetector
            filename: Optional filename for saving (without extension)
            
        Returns:
            Path to saved visualization image
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 16))
        
        # Original image
        axes[0, 0].imshow(image, cmap='gray')
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')
        
        # Horizontal lines
        axes[0, 1].imshow(image, cmap='gray')
        self._plot_lines(axes[0, 1], grid_info['horizontal_lines'], 'horizontal', 
                        image.shape, color='red')
        axes[0, 1].set_title(f'Horizontal Lines ({len(grid_info["horizontal_lines"])} detected)')
        axes[0, 1].axis('off')
        
        # Vertical lines
        axes[1, 0].imshow(image, cmap='gray')
        self._plot_lines(axes[1, 0], grid_info['vertical_lines'], 'vertical',
                        image.shape, color='blue')
        axes[1, 0].set_title(f'Vertical Lines ({len(grid_info["vertical_lines"])} detected)')
        axes[1, 0].axis('off')
        
        # All lines with intersections
        axes[1, 1].imshow(image, cmap='gray')
        self._plot_lines(axes[1, 1], grid_info['horizontal_lines'], 'horizontal',
                        image.shape, color='red', alpha=0.6)
        self._plot_lines(axes[1, 1], grid_info['vertical_lines'], 'vertical',
                        image.shape, color='blue', alpha=0.6)
        self._plot_intersections(axes[1, 1], grid_info['intersections'])
        axes[1, 1].set_title('Grid with Intersections')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        
        # Save figure
        if filename is None:
            filename = 'grid_visualization'
        
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _plot_lines(self, ax, lines: List[Dict], orientation: str, 
                   image_shape: Tuple[int, int], color: str = 'red', alpha: float = 1.0):
        """Plot polynomial lines on axes"""
        for i, line in enumerate(lines):
            func = line['function']
            x_min, x_max = line['domain']
            
            if orientation == 'horizontal':
                # y = f(x)
                x_plot = np.linspace(max(0, x_min), min(image_shape[1], x_max), 200)
                y_plot = func(x_plot)
                
                # Clip to image bounds
                valid = (y_plot >= 0) & (y_plot < image_shape[0])
                x_plot = x_plot[valid]
                y_plot = y_plot[valid]
                
                ax.plot(x_plot, y_plot, color=color, linewidth=1.5, alpha=alpha,
                       label=f"Degree {line['degree']}" if i == 0 else "")
            else:
                # x = f(y)
                y_plot = np.linspace(max(0, x_min), min(image_shape[0], x_max), 200)
                x_plot = func(y_plot)
                
                # Clip to image bounds
                valid = (x_plot >= 0) & (x_plot < image_shape[1])
                y_plot = y_plot[valid]
                x_plot = x_plot[valid]
                
                ax.plot(x_plot, y_plot, color=color, linewidth=1.5, alpha=alpha,
                       label=f"Degree {line['degree']}" if i == 0 else "")
    
    def _plot_intersections(self, ax, intersections: List[Dict]):
        """Plot grid intersections"""
        if not intersections:
            return
        
        x_coords = [int['x'] for int in intersections]
        y_coords = [int['y'] for int in intersections]
        
        ax.scatter(x_coords, y_coords, c='yellow', s=20, alpha=0.7, 
                  edgecolors='black', linewidths=0.5, zorder=10)
    
    def compare_polynomial_degrees(self, image: np.ndarray, grid_info: Dict,
                                   line_idx: int = 0, orientation: str = 'horizontal',
                                   filename: Optional[str] = None) -> str:
        """
        Compare different polynomial degrees for a single line
        
        Args:
            image: Original ECG image
            grid_info: Grid detection results
            line_idx: Index of line to compare
            orientation: 'horizontal' or 'vertical'
            filename: Optional filename for saving
            
        Returns:
            Path to saved comparison image
        """
        lines = grid_info[f'{orientation}_lines']
        if line_idx >= len(lines):
            raise ValueError(f"Line index {line_idx} out of range")
        
        line = lines[line_idx]
        func = line['function']
        x_min, x_max = line['domain']
        
        # Sample points along the line
        if orientation == 'horizontal':
            x_samples = np.linspace(x_min, x_max, 100)
            y_samples = func(x_samples)
            
            # Fit different degrees
            degrees_to_compare = [1, 2, 3]
            fits = {}
            for deg in degrees_to_compare:
                if deg <= len(x_samples) - 1:
                    coeffs = np.polyfit(x_samples, y_samples, deg)
                    fits[deg] = np.poly1d(coeffs)
        else:
            y_samples = np.linspace(x_min, x_max, 100)
            x_samples = func(y_samples)
            
            degrees_to_compare = [1, 2, 3]
            fits = {}
            for deg in degrees_to_compare:
                if deg <= len(y_samples) - 1:
                    coeffs = np.polyfit(y_samples, x_samples, deg)
                    fits[deg] = np.poly1d(coeffs)
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Original image with line
        axes[0].imshow(image, cmap='gray')
        if orientation == 'horizontal':
            x_plot = np.linspace(x_min, x_max, 200)
            y_plot = func(x_plot)
            axes[0].plot(x_plot, y_plot, 'r-', linewidth=2, label=f"Detected (degree {line['degree']})")
        else:
            y_plot = np.linspace(x_min, x_max, 200)
            x_plot = func(y_plot)
            axes[0].plot(x_plot, y_plot, 'r-', linewidth=2, label=f"Detected (degree {line['degree']})")
        axes[0].set_title(f'{orientation.capitalize()} Line Comparison')
        axes[0].axis('off')
        axes[0].legend()
        
        # Comparison plot
        if orientation == 'horizontal':
            x_plot = np.linspace(x_min, x_max, 200)
            axes[1].plot(x_samples, y_samples, 'ko', markersize=3, label='Sample points')
            for deg, fit_func in fits.items():
                y_fit = fit_func(x_plot)
                axes[1].plot(x_plot, y_fit, linewidth=2, label=f'Degree {deg}')
            axes[1].set_xlabel('X coordinate')
            axes[1].set_ylabel('Y coordinate')
        else:
            y_plot = np.linspace(x_min, x_max, 200)
            axes[1].plot(x_samples, y_samples, 'ko', markersize=3, label='Sample points')
            for deg, fit_func in fits.items():
                x_fit = fit_func(y_plot)
                axes[1].plot(x_fit, y_plot, linewidth=2, label=f'Degree {deg}')
            axes[1].set_xlabel('X coordinate')
            axes[1].set_ylabel('Y coordinate')
        
        axes[1].set_title('Polynomial Fit Comparison')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if filename is None:
            filename = f'polynomial_comparison_{orientation}_{line_idx}'
        
        output_path = os.path.join(self.output_dir, f"{filename}.png")
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def check_oscillation(self, grid_info: Dict, threshold: float = 5.0) -> Dict:
        """
        Check for oscillation in higher-order lines
        
        Args:
            grid_info: Grid detection results
            threshold: Maximum allowed deviation from linear fit (pixels)
            
        Returns:
            Dictionary with oscillation analysis results
        """
        results = {
            'horizontal_lines': [],
            'vertical_lines': [],
            'total_checked': 0,
            'oscillating_lines': 0
        }
        
        # Check horizontal lines
        for i, line in enumerate(grid_info['horizontal_lines']):
            if line['degree'] > 1:
                deviation = self._calculate_linear_deviation(line, 'horizontal', 
                                                             grid_info['image_shape'])
                is_oscillating = deviation > threshold
                results['horizontal_lines'].append({
                    'index': i,
                    'degree': line['degree'],
                    'max_deviation': deviation,
                    'oscillating': is_oscillating
                })
                results['total_checked'] += 1
                if is_oscillating:
                    results['oscillating_lines'] += 1
        
        # Check vertical lines
        for i, line in enumerate(grid_info['vertical_lines']):
            if line['degree'] > 1:
                deviation = self._calculate_linear_deviation(line, 'vertical',
                                                           grid_info['image_shape'])
                is_oscillating = deviation > threshold
                results['vertical_lines'].append({
                    'index': i,
                    'degree': line['degree'],
                    'max_deviation': deviation,
                    'oscillating': is_oscillating
                })
                results['total_checked'] += 1
                if is_oscillating:
                    results['oscillating_lines'] += 1
        
        return results
    
    def _calculate_linear_deviation(self, line: Dict, orientation: str,
                                   image_shape: Tuple[int, int]) -> float:
        """Calculate maximum deviation from linear fit"""
        func = line['function']
        x_min, x_max = line['domain']
        
        # Sample points
        num_samples = 100
        if orientation == 'horizontal':
            x_samples = np.linspace(x_min, x_max, num_samples)
            y_poly = func(x_samples)
            
            # Fit linear
            coeffs_linear = np.polyfit(x_samples, y_poly, 1)
            y_linear = np.polyval(coeffs_linear, x_samples)
            
            # Calculate deviation
            deviation = np.max(np.abs(y_poly - y_linear))
        else:
            y_samples = np.linspace(x_min, x_max, num_samples)
            x_poly = func(y_samples)
            
            # Fit linear
            coeffs_linear = np.polyfit(y_samples, x_poly, 1)
            x_linear = np.polyval(coeffs_linear, y_samples)
            
            # Calculate deviation
            deviation = np.max(np.abs(x_poly - x_linear))
        
        return float(deviation)
    
    def generate_oscillation_report(self, oscillation_results: Dict, 
                                   filename: Optional[str] = None) -> str:
        """
        Generate a text report of oscillation analysis
        
        Args:
            oscillation_results: Results from check_oscillation()
            filename: Optional filename for saving
            
        Returns:
            Path to saved report
        """
        report_lines = [
            "Grid Line Oscillation Analysis Report",
            "=" * 50,
            "",
            f"Total lines checked: {oscillation_results['total_checked']}",
            f"Oscillating lines: {oscillation_results['oscillating_lines']}",
            "",
            "Horizontal Lines:",
            "-" * 30
        ]
        
        for line_info in oscillation_results['horizontal_lines']:
            status = "OSCILLATING" if line_info['oscillating'] else "OK"
            report_lines.append(
                f"  Line {line_info['index']}: Degree {line_info['degree']}, "
                f"Max deviation: {line_info['max_deviation']:.2f} px - {status}"
            )
        
        report_lines.extend([
            "",
            "Vertical Lines:",
            "-" * 30
        ])
        
        for line_info in oscillation_results['vertical_lines']:
            status = "OSCILLATING" if line_info['oscillating'] else "OK"
            report_lines.append(
                f"  Line {line_info['index']}: Degree {line_info['degree']}, "
                f"Max deviation: {line_info['max_deviation']:.2f} px - {status}"
            )
        
        report_text = "\n".join(report_lines)
        
        if filename is None:
            filename = 'oscillation_report'
        
        output_path = os.path.join(self.output_dir, f"{filename}.txt")
        with open(output_path, 'w') as f:
            f.write(report_text)
        
        return output_path
