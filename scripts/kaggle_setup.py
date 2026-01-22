"""
Kaggle API Setup
Configure and test Kaggle API connection
"""

import os
import json
from pathlib import Path
from typing import Optional


def setup_kaggle_credentials(username: Optional[str] = None,
                            api_key: Optional[str] = None,
                            config_path: Optional[str] = None):
    """
    Setup Kaggle API credentials
    
    Args:
        username: Kaggle username
        api_key: Kaggle API key
        config_path: Path to kaggle.json (default: ~/.kaggle/kaggle.json)
    """
    if config_path is None:
        kaggle_dir = Path.home() / '.kaggle'
        config_path = kaggle_dir / 'kaggle.json'
    else:
        config_path = Path(config_path)
    
    # Create .kaggle directory if it doesn't exist
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get credentials from environment or parameters
    if not username:
        username = os.environ.get('KAGGLE_USERNAME')
    if not api_key:
        api_key = os.environ.get('KAGGLE_KEY')
    
    if not username or not api_key:
        raise ValueError(
            "Kaggle credentials not found. Please provide username and api_key, "
            "or set KAGGLE_USERNAME and KAGGLE_KEY environment variables, "
            "or place kaggle.json in ~/.kaggle/"
        )
    
    # Create kaggle.json
    config = {
        "username": username,
        "key": api_key
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    # Set permissions (Kaggle requires 600)
    os.chmod(config_path, 0o600)
    
    print(f"Kaggle credentials saved to {config_path}")
    return config_path


def test_kaggle_connection():
    """Test Kaggle API connection"""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        # Test by listing competitions
        competitions = api.competitions_list()
        print(f"✓ Kaggle API connection successful!")
        print(f"  Found {len(competitions)} competitions")
        
        return True
    except Exception as e:
        print(f"✗ Kaggle API connection failed: {e}")
        return False


def list_competition_datasets(competition_name: str = 'physionet-ecg-image-digitization'):
    """
    List datasets available for a competition
    
    Args:
        competition_name: Name of the competition
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        # List competition files
        files = api.competition_list_files(competition_name)
        
        print(f"Files available for competition '{competition_name}':")
        for file in files:
            print(f"  - {file.name} ({file.size / (1024**3):.2f} GB)")
        
        return files
    except Exception as e:
        print(f"Error listing competition files: {e}")
        return []


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            username = sys.argv[2] if len(sys.argv) > 2 else None
            api_key = sys.argv[3] if len(sys.argv) > 3 else None
            setup_kaggle_credentials(username, api_key)
        elif sys.argv[1] == "test":
            test_kaggle_connection()
        elif sys.argv[1] == "list":
            competition = sys.argv[2] if len(sys.argv) > 2 else 'physionet-ecg-image-digitization'
            list_competition_datasets(competition)
    else:
        print("Usage:")
        print("  python kaggle_setup.py setup [username] [api_key]")
        print("  python kaggle_setup.py test")
        print("  python kaggle_setup.py list [competition_name]")
