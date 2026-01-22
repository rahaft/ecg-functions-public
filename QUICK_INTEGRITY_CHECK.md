# Quick Kaggle Code Integrity Check

## 🚀 Quick Start

### 1. Check Current Code
```bash
# Run compliance checker (when implemented)
python -m src.utils.compliance --check-all
```

### 2. Before Every Edit
Ask yourself:
- ✅ Is this import allowed?
- ✅ Does this need internet? (If yes, STOP)
- ✅ Are paths environment-agnostic?
- ✅ Will this work offline?

### 3. Before Committing
```bash
# Git hook will auto-run (when set up)
git commit -m "your message"
# Hook will check compliance automatically
```

---

## 📋 Allowed vs Forbidden

### ✅ ALLOWED Imports
```python
import torch
import cv2
import numpy as np
import pandas as pd
from sklearn import ...
from scipy import ...
from PIL import Image
```

### ❌ FORBIDDEN Imports
```python
import requests      # NO internet
import urllib       # NO internet
import wget         # NO downloads
import socket       # NO network
```

### ✅ ALLOWED Patterns
```python
# Environment detection
ENV = get_environment()
MODEL_DIR = {'kaggle': '/kaggle/input/...', ...}[ENV]

# Load from local path
model = torch.load(f'{MODEL_DIR}/model.pth')
```

### ❌ FORBIDDEN Patterns
```python
# Internet access
model = requests.get('https://...')  # NO

# Hard-coded paths
MODEL_DIR = '/home/user/models'  # NO

# Package installation
subprocess.run(['pip', 'install', ...])  # NO
```

---

## 🎯 Cursor AI Integration

**Cursor automatically:**
- Reads `.cursorrules` file
- Warns on forbidden imports
- Protects critical files
- Suggests compliant code

**Just follow the prompts!**

---

## 📝 Protected Files

**DO NOT EDIT without permission:**
- `kaggle_submission/submission.py`
- `requirements_kaggle.txt`
- `src/utils/compliance.py`
- `src/utils/environment.py`

**Safe to edit:**
- `src/processors/*.py` (if marked editable)
- `src/config/hyperparams.yaml`
- `tests/*.py`

---

**Quick Reference - Keep this handy!**
