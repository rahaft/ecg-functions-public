"""
Simple Image Viewer
View processed images and results directly using matplotlib
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import numpy as np


def view_image(image_path: str):
    """View a single image"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    
    img = mpimg.imread(image_path)
    plt.figure(figsize=(12, 8))
    plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)
    plt.title(Path(image_path).name)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def view_directory(directory: str, pattern: str = '*.png'):
    """View all images in a directory"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Directory not found: {directory}")
        return
    
    images = list(dir_path.glob(pattern))
    
    if not images:
        print(f"No images found matching {pattern} in {directory}")
        return
    
    print(f"Found {len(images)} images")
    
    # Show first few images
    num_to_show = min(6, len(images))
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, img_path in enumerate(images[:num_to_show]):
        img = mpimg.imread(str(img_path))
        axes[i].imshow(img, cmap='gray' if len(img.shape) == 2 else None)
        axes[i].set_title(img_path.name, fontsize=8)
        axes[i].axis('off')
    
    # Hide unused subplots
    for i in range(num_to_show, 6):
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # Print list of all images
    print("\nAll images:")
    for img_path in images:
        print(f"  - {img_path.name}")


def view_test_results(results_dir: str = 'data/test_output'):
    """View test results"""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Results directory not found: {results_dir}")
        print("Run test first: python scripts/run_test.py test <image_path>")
        return
    
    # Find grid visualizations
    grid_images = list(results_path.glob('grid_*.png'))
    signal_images = list(results_path.glob('*_signals.png'))
    
    if not grid_images and not signal_images:
        print("No result images found")
        return
    
    # Show grid visualizations
    if grid_images:
        print(f"\nGrid Visualizations ({len(grid_images)} found):")
        for img_path in grid_images[:3]:  # Show first 3
            view_image(str(img_path))
    
    # Show signal plots
    if signal_images:
        print(f"\nSignal Plots ({len(signal_images)} found):")
        for img_path in signal_images[:3]:  # Show first 3
            view_image(str(img_path))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "dir":
            directory = sys.argv[2] if len(sys.argv) > 2 else 'data/test_output'
            view_directory(directory)
        elif sys.argv[1] == "results":
            results_dir = sys.argv[2] if len(sys.argv) > 2 else 'data/test_output'
            view_test_results(results_dir)
        else:
            # Treat as image path
            view_image(sys.argv[1])
    else:
        print("Usage:")
        print("  python simple_viewer.py <image_path>     - View single image")
        print("  python simple_viewer.py dir [directory] - View directory")
        print("  python simple_viewer.py results [dir]    - View test results")
