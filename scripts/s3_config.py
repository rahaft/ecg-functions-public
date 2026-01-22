"""
AWS S3 Configuration
Configure AWS S3 bucket and access settings
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict


class S3Config:
    """AWS S3 configuration"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize S3 configuration
        
        Args:
            config_path: Path to config file (default: s3_config.json)
        """
        if config_path is None:
            config_path = Path('scripts') / 's3_config.json'
        else:
            config_path = Path(config_path)
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or environment"""
        # Try to load from file
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Load from environment variables
        config = {
            'bucket_name': os.environ.get('AWS_S3_BUCKET'),
            'region': os.environ.get('AWS_REGION', 'us-east-1'),
            'access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
            'secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
            'path_prefix': os.environ.get('AWS_S3_PATH_PREFIX', 'ecg_competition')
        }
        
        return config
    
    def save_config(self, bucket_name: str,
                   region: str = 'us-east-1',
                   access_key_id: Optional[str] = None,
                   secret_access_key: Optional[str] = None,
                   path_prefix: str = 'ecg_competition'):
        """
        Save configuration to file
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
            access_key_id: AWS access key ID (optional, can use env var)
            secret_access_key: AWS secret access key (optional, can use env var)
            path_prefix: Path prefix in bucket
        """
        config = {
            'bucket_name': bucket_name,
            'region': region,
            'path_prefix': path_prefix
        }
        
        # Only save credentials if provided (prefer environment variables)
        if access_key_id:
            config['access_key_id'] = access_key_id
        if secret_access_key:
            config['secret_access_key'] = secret_access_key
        
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set restrictive permissions
        os.chmod(self.config_path, 0o600)
        
        print(f"Configuration saved to {self.config_path}")
        self.config = config
    
    def get_bucket_name(self) -> Optional[str]:
        """Get bucket name"""
        return self.config.get('bucket_name')
    
    def get_region(self) -> str:
        """Get AWS region"""
        return self.config.get('region', 'us-east-1')
    
    def get_path_prefix(self) -> str:
        """Get path prefix"""
        return self.config.get('path_prefix', 'ecg_competition')
    
    def get_credentials(self) -> Dict[str, Optional[str]]:
        """Get AWS credentials"""
        return {
            'aws_access_key_id': (
                self.config.get('access_key_id') or
                os.environ.get('AWS_ACCESS_KEY_ID')
            ),
            'aws_secret_access_key': (
                self.config.get('secret_access_key') or
                os.environ.get('AWS_SECRET_ACCESS_KEY')
            )
        }
    
    def validate(self) -> bool:
        """Validate configuration"""
        bucket_name = self.get_bucket_name()
        if not bucket_name:
            print("✗ Bucket name not configured")
            return False
        
        credentials = self.get_credentials()
        if not credentials['aws_access_key_id'] or not credentials['aws_secret_access_key']:
            print("✗ AWS credentials not configured")
            print("  Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
            return False
        
        print("✓ S3 configuration is valid")
        return True


def get_s3_path_structure() -> Dict[str, str]:
    """
    Get S3 path structure
    
    Returns:
        Dictionary with path templates
    """
    return {
        'raw_images': 'competition_data/raw_images',
        'processed_images': 'competition_data/processed_images',
        'metadata': 'competition_data/metadata',
        'digitized_signals': 'results/digitized_signals',
        'quality_reports': 'results/quality_reports',
        'submissions': 'results/submissions',
        'best_images': 'best_images/quality_ranked',
        'top_10': 'best_images/top_10'
    }


if __name__ == "__main__":
    import sys
    
    config = S3Config()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            bucket = sys.argv[2] if len(sys.argv) > 2 else None
            region = sys.argv[3] if len(sys.argv) > 3 else 'us-east-1'
            
            if not bucket:
                print("Usage: python s3_config.py setup <bucket_name> [region]")
            else:
                config.save_config(bucket, region)
        elif sys.argv[1] == "validate":
            config.validate()
        elif sys.argv[1] == "paths":
            paths = get_s3_path_structure()
            print("S3 Path Structure:")
            for key, path in paths.items():
                print(f"  {key}: {path}")
    else:
        print("Usage:")
        print("  python s3_config.py setup <bucket_name> [region]")
        print("  python s3_config.py validate")
        print("  python s3_config.py paths")
