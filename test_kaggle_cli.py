#!/usr/bin/env python3
"""Test Kaggle using direct HTTP requests instead of SDK"""

import requests
import json
import os
from pathlib import Path

# Load credentials
kaggle_file = Path.home() / '.kaggle' / 'kaggle.json'

if kaggle_file.exists():
    with open(kaggle_file, 'r') as f:
        config = json.load(f)
        username = config.get('username')
        key = config.get('key')
        print(f"Username: {username}")
        print(f"Key: {key[:20]}...")
else:
    print("kaggle.json not found!")
    exit(1)

# Try direct API call with basic auth
competition_name = "physionet-ecg-image-digitization"

# Method 1: Try with Basic Auth (username:key)
print("\n--- Testing with Basic Auth (username:key) ---")
try:
    url = f"https://www.kaggle.com/api/v1/competitions/data/list/{competition_name}"
    response = requests.get(url, auth=(username, key))
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        files = response.json()
        print(f"Success! Found {len(files)} files")
        for f in files[:5]:
            print(f"  - {f.get('name', f)}")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Method 2: Try with token in header
print("\n--- Testing with Bearer Token ---")
try:
    url = f"https://www.kaggle.com/api/v1/competitions/data/list/{competition_name}"
    headers = {"Authorization": f"Bearer {key}"}
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        files = response.json()
        print(f"Success! Found {len(files)} files")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Method 3: Try listing competitions (public endpoint)
print("\n--- Testing public endpoint (list competitions) ---")
try:
    url = "https://www.kaggle.com/api/v1/competitions/list"
    response = requests.get(url, auth=(username, key))
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        competitions = response.json()
        print(f"Success! Can access API. Found {len(competitions)} competitions")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
