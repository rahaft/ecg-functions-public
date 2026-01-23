"""
Simple Test Script for Kaggle Notebook
Copy this into a new cell to test images and get SNR

Usage:
    result = test_image('path/to/image.jpg')
    print(f"SNR: {result['mean_snr']:.2f} dB")
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']


def test_image(image_path: str, show_plot: bool = True) -> dict:
    """Test a single image and return results with SNR"""
    print(f"Testing: {image_path}")
    
    # Process image
    digitizer = ECGDigitizer(use_segmented_processing=True, enable_visualization=False)
    result = digitizer.process_image(image_path)
    
    # Get SNR from quality metrics
    quality = result.get('metadata', {}).get('quality', {})
    mean_snr = quality.get('mean_snr', 0)
    min_snr = quality.get('min_snr', 0)
    
    print(f"✓ Mean SNR: {mean_snr:.2f} dB (min: {min_snr:.2f} dB)")
    
    # Plot if requested
    if show_plot:
        plot_signals(result['leads'])
    
    return {
        'mean_snr': mean_snr,
        'min_snr': min_snr,
        'signals': result['leads'],
        'quality': quality
    }


def plot_signals(leads: list):
    """Plot all 12 leads"""
    fig, axes = plt.subplots(4, 3, figsize=(15, 12))
    axes = axes.flatten()
    
    for idx, lead_data in enumerate(leads):
        if idx >= 12:
            break
        ax = axes[idx]
        signal = np.array(lead_data['values'])
        time = np.arange(len(signal)) / 500
        ax.plot(time, signal)
        ax.set_title(f"Lead {lead_data['name']}")
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


# Quick test function
def quick_test(image_path: str):
    """Quick test - just print SNR"""
    result = test_image(image_path, show_plot=False)
    print(f"\nSNR: {result['mean_snr']:.2f} dB")
    return result
