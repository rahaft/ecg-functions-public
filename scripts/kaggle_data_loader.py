"""
Kaggle Data Loader
Stream competition data directly from Kaggle without full download
"""

import os
import io
from pathlib import Path
from typing import List, Optional, Iterator, Tuple
import numpy as np
from PIL import Image
import requests
from tqdm import tqdm


class KaggleDataLoader:
    """Load competition data directly from Kaggle API"""
    
    def __init__(self, competition_name: str = 'physionet-ecg-image-digitization',
                 cache_dir: Optional[str] = None):
        """
        Initialize Kaggle data loader
        
        Args:
            competition_name: Name of the competition
            cache_dir: Directory to cache downloaded files (optional)
        """
        self.competition_name = competition_name
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Kaggle API
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            self.api = KaggleApi()
            self.api.authenticate()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Kaggle API: {e}")
    
    def list_files(self) -> List[dict]:
        """List all files in the competition"""
        files = self.api.competition_list_files(self.competition_name)
        return [
            {
                'name': f.name,
                'size': f.size,
                'creationDate': f.creationDate
            }
            for f in files
        ]
    
    def download_file(self, filename: str, 
                     output_path: Optional[str] = None,
                     use_cache: bool = True) -> str:
        """
        Download a single file from competition
        
        Args:
            filename: Name of file to download
            output_path: Optional output path (uses cache_dir if None)
            use_cache: Use cached file if available
            
        Returns:
            Path to downloaded file
        """
        if output_path is None:
            if self.cache_dir:
                output_path = self.cache_dir / filename
            else:
                output_path = Path(filename)
        else:
            output_path = Path(output_path)
        
        # Check cache
        if use_cache and output_path.exists():
            print(f"Using cached file: {output_path}")
            return str(output_path)
        
        # Download file
        print(f"Downloading {filename}...")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.api.competition_download_file(
            self.competition_name,
            filename,
            path=str(output_path.parent),
            quiet=False
        )
        
        # Move to correct location if needed
        downloaded_path = output_path.parent / filename
        if downloaded_path != output_path:
            downloaded_path.rename(output_path)
        
        return str(output_path)
    
    def stream_image(self, filename: str) -> Iterator[bytes]:
        """
        Stream an image file without downloading fully
        
        Args:
            filename: Name of image file
            
        Yields:
            Chunks of image data
        """
        # Get download URL (this is a simplified approach)
        # In practice, you may need to use Kaggle API's download methods
        # For large files, consider downloading in chunks
        
        file_path = self.download_file(filename, use_cache=True)
        
        # Stream file in chunks
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)  # 8KB chunks
                if not chunk:
                    break
                yield chunk
    
    def load_image(self, filename: str) -> np.ndarray:
        """
        Load an image file as numpy array
        
        Args:
            filename: Name of image file
            
        Returns:
            Image as numpy array
        """
        file_path = self.download_file(filename, use_cache=True)
        
        # Load image
        img = Image.open(file_path)
        img_array = np.array(img)
        
        return img_array
    
    def get_image_list(self, file_pattern: str = '*.jpg') -> List[str]:
        """
        Get list of image files matching pattern
        
        Args:
            file_pattern: File pattern to match (e.g., '*.jpg', 'train/*.png')
            
        Returns:
            List of matching filenames
        """
        all_files = self.list_files()
        
        # Simple pattern matching (can be enhanced)
        if '*' in file_pattern:
            pattern = file_pattern.replace('*', '')
            matching = [f['name'] for f in all_files if pattern in f['name']]
        else:
            matching = [f['name'] for f in all_files if f['name'] == file_pattern]
        
        return matching
    
    def download_batch(self, filenames: List[str],
                      output_dir: Optional[str] = None,
                      use_cache: bool = True) -> List[str]:
        """
        Download multiple files
        
        Args:
            filenames: List of filenames to download
            output_dir: Optional output directory
            use_cache: Use cached files if available
            
        Returns:
            List of paths to downloaded files
        """
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        elif self.cache_dir:
            output_dir = self.cache_dir
        else:
            output_dir = Path('.')
        
        downloaded_paths = []
        
        for filename in tqdm(filenames, desc="Downloading files"):
            output_path = output_dir / filename
            path = self.download_file(filename, str(output_path), use_cache)
            downloaded_paths.append(path)
        
        return downloaded_paths
    
    def get_metadata(self, filename: str = 'metadata.csv') -> Optional[dict]:
        """
        Load metadata file if available
        
        Args:
            filename: Name of metadata file
            
        Returns:
            Metadata dictionary or None
        """
        try:
            import pandas as pd
            file_path = self.download_file(filename, use_cache=True)
            return pd.read_csv(file_path).to_dict('records')
        except Exception as e:
            print(f"Could not load metadata: {e}")
            return None


if __name__ == "__main__":
    import sys
    
    loader = KaggleDataLoader()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            files = loader.list_files()
            for f in files:
                print(f"{f['name']} ({f['size'] / (1024**2):.2f} MB)")
        elif sys.argv[1] == "download":
            filename = sys.argv[2] if len(sys.argv) > 2 else None
            if filename:
                path = loader.download_file(filename)
                print(f"Downloaded to: {path}")
            else:
                print("Usage: python kaggle_data_loader.py download <filename>")
    else:
        print("Usage:")
        print("  python kaggle_data_loader.py list")
        print("  python kaggle_data_loader.py download <filename>")
