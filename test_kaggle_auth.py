#!/usr/bin/env python3
"""Test Kaggle authentication"""

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    import json
    from pathlib import Path
    
    # Check if credentials file exists
    kaggle_file = Path.home() / '.kaggle' / 'kaggle.json'
    if kaggle_file.exists():
        with open(kaggle_file, 'r') as f:
            config = json.load(f)
            print(f"✓ Credentials file found")
            print(f"  Username: {config.get('username', 'MISSING')}")
            print(f"  Key: {config.get('key', 'MISSING')[:20]}...")
    else:
        print("✗ Credentials file not found")
        exit(1)
    
    # Try to authenticate
    api = KaggleApi()
    print("\nAttempting authentication...")
    api.authenticate()
    print("✓ Authentication successful!")
    
    # Try to list competitions
    print("\nTesting API access...")
    competitions = api.competition_list()
    print(f"✓ Can list competitions: Found {len(competitions)} competitions")
    
    # Check if we can access the specific competition
    competition_name = "physionet-ecg-image-digitization"
    print(f"\nChecking competition: {competition_name}")
    
    try:
        comp_details = api.competition_list(search=competition_name)
        if comp_details:
            print(f"✓ Competition found: {comp_details[0].title}")
        else:
            print(f"⚠ Competition not found in search results")
    except Exception as e:
        print(f"Error checking competition: {e}")
    
    # Try to list files
    print(f"\nAttempting to list files...")
    try:
        files = api.competition_list_files(competition_name)
        print(f"✓ Success! Found {len(files)} files")
        print(f"\nFirst 5 files:")
        for f in files[:5]:
            print(f"  - {f.name} ({f.size} bytes)")
    except Exception as e:
        print(f"✗ Error listing files: {e}")
        if "401" in str(e):
            print("\n⚠ 401 Unauthorized - Possible reasons:")
            print("  1. Competition terms not accepted")
            print("     Go to: https://www.kaggle.com/competitions/physionet-ecg-image-digitization/rules")
            print("     Click 'I Understand and Accept'")
            print("  2. Invalid or expired token")
            print("     Generate a new token at: https://www.kaggle.com/account")
            print("  3. Token format incorrect")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
