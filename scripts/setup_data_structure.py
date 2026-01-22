"""
Setup Data Structure
Create directory structure for organizing competition files
"""

import os
from pathlib import Path
from typing import Optional


def create_data_structure(base_dir: str = 'data'):
    """
    Create directory structure for competition data
    
    Args:
        base_dir: Base directory for data structure
    """
    base_path = Path(base_dir)
    
    directories = [
        'cache',           # Cached images from Kaggle
        'processed',      # Processed images
        'results',        # Digitization results
        'best_images',    # Selected best images
        'submissions',    # Competition submission files
        'visualizations', # Line visualization outputs
        'raw'             # Raw competition images (if downloaded)
    ]
    
    for dir_name in directories:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Create .gitkeep files to preserve empty directories
    for dir_name in directories:
        gitkeep = base_path / dir_name / '.gitkeep'
        if not gitkeep.exists():
            gitkeep.touch()
    
    print(f"\nData structure created in: {base_path.absolute()}")
    return base_path


def validate_data_structure(base_dir: str = 'data') -> bool:
    """
    Validate that data structure exists
    
    Args:
        base_dir: Base directory for data structure
        
    Returns:
        True if structure is valid
    """
    base_path = Path(base_dir)
    
    required_dirs = [
        'cache',
        'processed',
        'results',
        'best_images',
        'submissions',
        'visualizations'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"Missing directories: {missing_dirs}")
        return False
    
    print("Data structure is valid")
    return True


def check_kaggle_setup() -> bool:
    """Check if Kaggle API is set up"""
    kaggle_config = Path.home() / '.kaggle' / 'kaggle.json'
    
    if kaggle_config.exists():
        print(f"✓ Kaggle credentials found: {kaggle_config}")
        return True
    else:
        print(f"✗ Kaggle credentials not found: {kaggle_config}")
        print("  Run: python scripts/kaggle_setup.py setup <username> <api_key>")
        return False


if __name__ == "__main__":
    import sys
    
    base_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    
    print("Setting up data structure...")
    create_data_structure(base_dir)
    
    print("\nValidating data structure...")
    validate_data_structure(base_dir)
    
    print("\nChecking Kaggle setup...")
    check_kaggle_setup()
    
    print("\nSetup complete!")
