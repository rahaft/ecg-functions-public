#!/usr/bin/env python3
"""Test Google Cloud Storage authentication"""

try:
    from google.cloud import storage
    client = storage.Client(project='hv-ecg')
    print('✓ Authentication successful!')
    print(f'✓ Connected to project: {client.project}')
except Exception as e:
    print(f'Error: {e}')
    exit(1)
