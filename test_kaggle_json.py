#!/usr/bin/env python3
"""Test Kaggle JSON file"""

import json
import os
from pathlib import Path

kaggle_file = Path.home() / '.kaggle' / 'kaggle.json'

print(f"Checking: {kaggle_file}")
print(f"Exists: {kaggle_file.exists()}")

if kaggle_file.exists():
    with open(kaggle_file, 'r') as f:
        content = f.read()
        print(f"\nFile content:\n{content}")
        print(f"\nFile length: {len(content)} bytes")
        
        try:
            config = json.loads(content)
            print(f"\nJSON parsed successfully:")
            print(f"  username: {config.get('username', 'MISSING')}")
            print(f"  key: {config.get('key', 'MISSING')[:20]}...")
        except Exception as e:
            print(f"\nJSON parse error: {e}")
