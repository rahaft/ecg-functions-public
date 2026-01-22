"""
Upload to S3
Upload images and results to AWS S3
"""

import os
from pathlib import Path
from typing import List, Optional, Dict
from tqdm import tqdm
import boto3
from botocore.exceptions import ClientError

# Import S3 config
import sys
sys.path.append(str(Path(__file__).parent))
from s3_config import S3Config, get_s3_path_structure


class S3Uploader:
    """Upload files to AWS S3"""
    
    def __init__(self, config: Optional[S3Config] = None):
        """
        Initialize S3 uploader
        
        Args:
            config: Optional S3Config instance
        """
        if config is None:
            config = S3Config()
        
        self.config = config
        
        if not config.validate():
            raise ValueError("S3 configuration is invalid")
        
        # Initialize S3 client
        credentials = config.get_credentials()
        self.s3_client = boto3.client(
            's3',
            region_name=config.get_region(),
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key']
        )
        
        self.bucket_name = config.get_bucket_name()
        self.path_prefix = config.get_path_prefix()
        self.path_structure = get_s3_path_structure()
    
    def upload_file(self, local_path: str, s3_key: str,
                   content_type: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> bool:
        """
        Upload a single file to S3
        
        Args:
            local_path: Local file path
            s3_key: S3 object key
            content_type: Optional content type
            metadata: Optional metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
            
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            return True
        except ClientError as e:
            print(f"Error uploading {local_path}: {e}")
            return False
    
    def upload_directory(self, local_dir: str, s3_prefix: str,
                       file_pattern: str = '*',
                       recursive: bool = True) -> List[str]:
        """
        Upload directory contents to S3
        
        Args:
            local_dir: Local directory path
            s3_prefix: S3 key prefix
            file_pattern: File pattern to match
            recursive: Upload recursively
        
        Returns:
            List of uploaded S3 keys
        """
        local_path = Path(local_dir)
        if not local_path.exists():
            raise ValueError(f"Directory does not exist: {local_dir}")
        
        uploaded_keys = []
        
        # Find files
        if recursive:
            files = list(local_path.rglob(file_pattern))
        else:
            files = list(local_path.glob(file_pattern))
        
        # Filter to only files (not directories)
        files = [f for f in files if f.is_file()]
        
        for file_path in tqdm(files, desc="Uploading files"):
            # Calculate relative path
            relative_path = file_path.relative_to(local_path)
            s3_key = f"{s3_prefix}/{relative_path}".replace('\\', '/')
            
            # Determine content type
            content_type = self._guess_content_type(file_path)
            
            if self.upload_file(str(file_path), s3_key, content_type):
                uploaded_keys.append(s3_key)
        
        return uploaded_keys
    
    def upload_image(self, image_path: str, category: str = 'raw_images',
                    image_id: Optional[str] = None) -> Optional[str]:
        """
        Upload an image file
        
        Args:
            image_path: Path to image file
            category: Category (raw_images, processed_images, etc.)
            image_id: Optional image identifier
        
        Returns:
            S3 key if successful, None otherwise
        """
        if category not in self.path_structure:
            raise ValueError(f"Unknown category: {category}")
        
        file_path = Path(image_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Generate S3 key
        if image_id:
            filename = f"{image_id}{file_path.suffix}"
        else:
            filename = file_path.name
        
        s3_key = f"{self.path_prefix}/{self.path_structure[category]}/{filename}"
        
        content_type = self._guess_content_type(file_path)
        
        if self.upload_file(str(file_path), s3_key, content_type):
            return s3_key
        
        return None
    
    def upload_results(self, results_dir: str, 
                      category: str = 'digitized_signals') -> List[str]:
        """
        Upload processing results
        
        Args:
            results_dir: Directory containing results
            category: Category (digitized_signals, quality_reports, etc.)
        
        Returns:
            List of uploaded S3 keys
        """
        s3_prefix = f"{self.path_prefix}/{self.path_structure.get(category, category)}"
        return self.upload_directory(results_dir, s3_prefix)
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for S3 object
        
        Args:
            s3_key: S3 object key
            expiration: Expiration time in seconds
        
        Returns:
            Presigned URL or None
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def _guess_content_type(self, file_path: Path) -> Optional[str]:
        """Guess content type from file extension"""
        extension = file_path.suffix.lower()
        
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.txt': 'text/plain',
            '.pdf': 'application/pdf'
        }
        
        return content_types.get(extension)


if __name__ == "__main__":
    import sys
    
    uploader = S3Uploader()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "upload":
            if len(sys.argv) < 3:
                print("Usage: python upload_to_s3.py upload <file_or_dir> [category]")
            else:
                path = sys.argv[2]
                category = sys.argv[3] if len(sys.argv) > 3 else 'raw_images'
                
                if os.path.isfile(path):
                    s3_key = uploader.upload_image(path, category)
                    if s3_key:
                        print(f"Uploaded to: s3://{uploader.bucket_name}/{s3_key}")
                elif os.path.isdir(path):
                    keys = uploader.upload_directory(path, f"{uploader.path_prefix}/{category}")
                    print(f"Uploaded {len(keys)} files")
                else:
                    print(f"Path not found: {path}")
        elif sys.argv[1] == "url":
            if len(sys.argv) < 3:
                print("Usage: python upload_to_s3.py url <s3_key>")
            else:
                s3_key = sys.argv[2]
                url = uploader.generate_presigned_url(s3_key)
                if url:
                    print(f"Presigned URL: {url}")
    else:
        print("Usage:")
        print("  python upload_to_s3.py upload <file_or_dir> [category]")
        print("  python upload_to_s3.py url <s3_key>")
