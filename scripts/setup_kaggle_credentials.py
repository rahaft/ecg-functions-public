"""
Setup Kaggle API Credentials
Quick script to configure Kaggle API token
"""

import os
import json
from pathlib import Path

# Your Kaggle API token from the image
KAGGLE_USERNAME = "raconcilio"  # From the image
KAGGLE_API_TOKEN = "KGAT_63eff21566308d9247d9336796c43581"  # From the image

def setup_kaggle_credentials():
    """Setup Kaggle credentials"""
    # Create .kaggle directory
    kaggle_dir = Path.home() / '.kaggle'
    kaggle_dir.mkdir(exist_ok=True)
    
    # Create kaggle.json
    config_path = kaggle_dir / 'kaggle.json'
    config = {
        "username": KAGGLE_USERNAME,
        "key": KAGGLE_API_TOKEN
    }
    
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    # Set permissions (important for Kaggle API)
    if os.name != 'nt':  # Unix-like systems
        os.chmod(config_path, 0o600)
    
    print(f"OK Kaggle credentials saved to: {config_path}")
    print(f"  Username: {KAGGLE_USERNAME}")
    print(f"  Token: {KAGGLE_API_TOKEN[:10]}...")
    
    # Also set as environment variable
    os.environ['KAGGLE_USERNAME'] = KAGGLE_USERNAME
    os.environ['KAGGLE_KEY'] = KAGGLE_API_TOKEN
    
    print("\nOK Environment variables set for this session")
    print("  To make them permanent, add to your system environment variables")
    
    return config_path

def test_kaggle_connection():
    """Test Kaggle API connection"""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        print("\nOK Kaggle API connection successful!")
        
        # List competitions
        competitions = api.competitions_list()
        print(f"  Found {len(competitions)} competitions")
        
        return True
    except Exception as e:
        print(f"\nERROR Kaggle API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Kaggle API credentials...")
    print("=" * 60)
    
    setup_kaggle_credentials()
    test_kaggle_connection()
    
    print("\n" + "=" * 60)
    print("Setup complete! You can now use Kaggle API to fetch images.")
