"""
Data Loader Module
Handle competition data structure with Kaggle API integration
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Iterator
import numpy as np
from PIL import Image

# Import Kaggle loader if available
try:
    import sys
    sys.path.append(str(Path(__file__).parent.parent / 'scripts'))
    from kaggle_data_loader import KaggleDataLoader
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False
    KaggleDataLoader = None


class CompetitionDataLoader:
    """Load and organize competition data"""
    
    def __init__(self, data_source: str = 'kaggle',
                competition_name: str = 'physionet-ecg-image-digitization',
                local_dir: Optional[str] = None,
                cache_dir: Optional[str] = None):
        """
        Initialize data loader
        
        Args:
            data_source: 'kaggle' or 'local'
            competition_name: Competition name for Kaggle
            local_dir: Local directory path (for 'local' source)
            cache_dir: Cache directory for Kaggle downloads
        """
        self.data_source = data_source
        self.competition_name = competition_name
        self.local_dir = Path(local_dir) if local_dir else None
        self.cache_dir = Path(cache_dir) if cache_dir else Path('data/cache')
        
        if data_source == 'kaggle':
            if not KAGGLE_AVAILABLE:
                raise RuntimeError(
                    "Kaggle API not available. Install kaggle package and set up credentials."
                )
            self.kaggle_loader = KaggleDataLoader(
                competition_name=competition_name,
                cache_dir=str(self.cache_dir)
            )
        else:
            self.kaggle_loader = None
            if not self.local_dir or not self.local_dir.exists():
                raise ValueError(f"Local directory does not exist: {local_dir}")
    
    def list_images(self, subset: str = 'train') -> List[str]:
        """
        List available images
        
        Args:
            subset: 'train', 'test', or 'all'
            
        Returns:
            List of image filenames
        """
        if self.data_source == 'kaggle':
            all_files = self.kaggle_loader.list_files()
            image_files = [
                f['name'] for f in all_files
                if f['name'].endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff'))
            ]
            
            # Filter by subset if specified
            if subset != 'all':
                image_files = [f for f in image_files if subset in f.lower()]
            
            return image_files
        else:
            # Local directory
            image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
            image_files = []
            
            search_dir = self.local_dir / subset if (self.local_dir / subset).exists() else self.local_dir
            
            for ext in image_extensions:
                image_files.extend(search_dir.glob(f'*{ext}'))
                image_files.extend(search_dir.glob(f'*{ext.upper()}'))
            
            return [str(f.relative_to(self.local_dir)) for f in image_files]
    
    def load_image(self, filename: str) -> np.ndarray:
        """
        Load an image as numpy array
        
        Args:
            filename: Image filename
            
        Returns:
            Image as numpy array
        """
        if self.data_source == 'kaggle':
            return self.kaggle_loader.load_image(filename)
        else:
            # Local file
            file_path = self.local_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(f"Image not found: {file_path}")
            
            img = Image.open(file_path)
            return np.array(img)
    
    def get_image_path(self, filename: str) -> str:
        """
        Get path to image file (downloads if needed for Kaggle)
        
        Args:
            filename: Image filename
            
        Returns:
            Path to image file
        """
        if self.data_source == 'kaggle':
            return self.kaggle_loader.download_file(filename, use_cache=True)
        else:
            file_path = self.local_dir / filename
            if not file_path.exists():
                raise FileNotFoundError(f"Image not found: {file_path}")
            return str(file_path)
    
    def load_ground_truth(self, image_id: str) -> Optional[Dict]:
        """
        Load ground truth data for an image (if available)
        
        Args:
            image_id: Image identifier
            
        Returns:
            Ground truth dictionary or None
        """
        # This would need to be implemented based on competition format
        # For now, return None
        return None
    
    def get_train_test_split(self, train_ratio: float = 0.8) -> Tuple[List[str], List[str]]:
        """
        Get train/test split of images
        
        Args:
            train_ratio: Ratio of training images
            
        Returns:
            (train_images, test_images) tuple
        """
        all_images = self.list_images('all')
        
        # Shuffle
        np.random.seed(42)
        np.random.shuffle(all_images)
        
        split_idx = int(len(all_images) * train_ratio)
        train_images = all_images[:split_idx]
        test_images = all_images[split_idx:]
        
        return train_images, test_images
    
    def iterate_images(self, subset: str = 'train',
                      batch_size: int = 1) -> Iterator[List[tuple]]:
        """
        Iterate over images in batches
        
        Args:
            subset: 'train', 'test', or 'all'
            batch_size: Number of images per batch
            
        Yields:
            List of (filename, image_array) tuples
        """
        image_files = self.list_images(subset)
        
        for i in range(0, len(image_files), batch_size):
            batch_files = image_files[i:i+batch_size]
            batch = []
            
            for filename in batch_files:
                try:
                    image = self.load_image(filename)
                    batch.append((filename, image))
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue
            
            if batch:
                yield batch


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        source = sys.argv[1]
        loader = CompetitionDataLoader(data_source=source)
        
        if len(sys.argv) > 2 and sys.argv[2] == "list":
            images = loader.list_images()
            print(f"Found {len(images)} images")
            for img in images[:10]:  # Show first 10
                print(f"  - {img}")
    else:
        print("Usage: python data_loader.py [kaggle|local] [list]")
