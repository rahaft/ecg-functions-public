#!/usr/bin/env python3
"""Test Kaggle API file listing"""

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    
    api = KaggleApi()
    api.authenticate()
    
    competition_name = "physionet-ecg-image-digitization"
    print(f"Fetching files from competition: {competition_name}")
    
    files = api.competition_list_files(competition_name)
    
    print(f"\nFound {len(files)} total files")
    
    # Check for images
    image_files = [f for f in files if any(f.name.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tif', '.tiff'])]
    
    print(f"Found {len(image_files)} image files")
    
    if len(image_files) > 0:
        print("\nFirst 10 image files:")
        for f in image_files[:10]:
            print(f"  - {f.name} ({f.size} bytes)")
    else:
        print("\nNo image files found. Listing all files:")
        for f in files[:20]:
            print(f"  - {f.name} ({f.size} bytes, ext: {f.name.split('.')[-1] if '.' in f.name else 'none'})")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
