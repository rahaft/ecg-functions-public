# Kaggle Code Integrity Guide

## 🎯 Purpose

This guide ensures all code maintains integrity for Kaggle submission. Kaggle has **strict offline requirements** - code must work without internet access.

---

## 🔒 Critical Rules

### 1. **No Internet Access**
- ❌ No `requests`, `urllib`, `wget`
- ❌ No API calls
- ❌ No model downloads
- ✅ All models pre-uploaded to Kaggle Datasets

### 2. **Allowed Packages Only**
**ONLY these packages:**
- `torch`, `torchvision`
- `cv2` (OpenCV)
- `numpy`, `pandas`
- `sklearn`, `scipy`, `skimage`
- `PIL` (Pillow)
- `matplotlib` (visualization only)

### 3. **Environment-Agnostic Paths**
- ✅ Use environment detection
- ❌ No hard-coded paths
- ❌ No URLs

### 4. **Protected Files**
- `kaggle_submission/submission.py`
- `requirements_kaggle.txt`
- `src/utils/compliance.py`
- `src/utils/environment.py`

---

## 📁 File Structure

```
hat_ecg/
├── .cursorrules                    # Cursor AI rules (THIS FILE)
├── .cursor/
│   └── rules.json                  # Cursor IDE rules (optional)
├── kaggle_submission/              # [PROTECTED]
│   └── submission.py               # Main Kaggle kernel
├── src/
│   ├── utils/
│   │   ├── compliance.py           # [PROTECTED] Compliance checker
│   │   └── environment.py          # [PROTECTED] Environment detection
│   └── processors/                 # [EDITABLE] Processing logic
├── requirements_kaggle.txt         # [PROTECTED] Kaggle packages
└── tests/
    └── test_offline.py             # Offline mode tests
```

---

## 🛡️ Protection Mechanisms

### 1. Cursor AI Rules (`.cursorrules`)

**Location:** `.cursorrules` in project root

**What it does:**
- Instructs Cursor AI to check imports before suggesting code
- Warns about forbidden patterns
- Protects critical files

**How to use:**
- Cursor automatically reads this file
- AI will warn/error on violations
- Follow the prompts

### 2. Compliance Checker

**Location:** `src/utils/compliance.py` (to be created)

**What it does:**
- Scans code for forbidden imports
- Checks for internet calls
- Validates file paths
- Verifies submission format

**Usage:**
```bash
python -m src.utils.compliance --check-all
```

### 3. Git Pre-commit Hook

**Location:** `.git/hooks/pre-commit`

**What it does:**
- Runs compliance checker before commit
- Blocks commits with violations
- Ensures code integrity

**Setup:**
```bash
chmod +x .git/hooks/pre-commit
```

### 4. Protected File Markers

**In code comments:**
```python
# [KAGGLE_COMPLIANT] - This code is verified for Kaggle
# [PROTECTED] - Do not edit without permission
# [EDITABLE] - Safe to modify
```

---

## ✅ Safe Editing Checklist

Before editing ANY code:

- [ ] Is this import in the allowed list?
- [ ] Does this require internet? (If yes, REJECT)
- [ ] Are paths environment-agnostic?
- [ ] Is this file protected? (If yes, ask permission)
- [ ] Will this work offline?
- [ ] Does this match Kaggle kernel constraints?

---

## 🚨 Red Flags

**STOP and ASK if you see:**
- `import requests` → Internet access forbidden
- `pip install` → No package installation
- `download()` → No downloads
- Hard-coded URL → Use environment detection
- New package import → Verify Kaggle compatibility

---

## 📝 Code Review Process

**Before committing:**

1. **Run compliance checker:**
   ```bash
   python -m src.utils.compliance --check-all
   ```

2. **Test offline mode:**
   ```bash
   python -m tests.test_offline
   ```

3. **Verify environment detection:**
   ```bash
   python -c "from src.utils.environment import get_environment; print(get_environment())"
   ```

4. **Check submission format:**
   ```bash
   python -m src.utils.submission_validator --validate submission.csv
   ```

---

## 🎯 Example: Correct vs Wrong

### ❌ WRONG:
```python
import requests  # FORBIDDEN
import wget      # FORBIDDEN

# Download model from internet
model_url = 'https://example.com/model.pth'
model = requests.get(model_url).content  # FORBIDDEN

# Hard-coded path
MODEL_DIR = '/home/user/models'  # FORBIDDEN
```

### ✅ CORRECT:
```python
import torch  # ALLOWED
import cv2    # ALLOWED

# Environment detection
from src.utils.environment import get_environment

ENV = get_environment()
MODEL_DIR = {
    'kaggle': '/kaggle/input/ecg-models',
    'colab': '/content/drive/MyDrive/ECG/models',
    'local': './models'
}[ENV]

# Load from local path (pre-uploaded)
model = torch.load(f'{MODEL_DIR}/model.pth')  # CORRECT
```

---

## 🔧 Setup Instructions

### 1. Create `.cursorrules` File

Already created in project root. Cursor will automatically use it.

### 2. Create Compliance Checker

**File:** `src/utils/compliance.py`

```python
"""
Kaggle Compliance Checker
Scans code for violations of Kaggle submission rules
"""

import ast
import re
from pathlib import Path
from typing import List, Dict

FORBIDDEN_IMPORTS = [
    'requests', 'urllib', 'urllib3', 'wget',
    'socket', 'http.client', 'httplib'
]

ALLOWED_IMPORTS = [
    'torch', 'torchvision', 'cv2', 'numpy', 'pandas',
    'sklearn', 'matplotlib', 'scipy', 'skimage', 'PIL'
]

def check_imports(file_path: Path) -> List[str]:
    """Check for forbidden imports"""
    violations = []
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in FORBIDDEN_IMPORTS:
                        violations.append(f"Forbidden import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in FORBIDDEN_IMPORTS:
                    violations.append(f"Forbidden import: {node.module}")
    return violations

def check_internet_calls(file_path: Path) -> List[str]:
    """Check for internet access calls"""
    violations = []
    patterns = [
        r'requests\.(get|post|put|delete)',
        r'urllib\.request\.urlopen',
        r'wget\.download',
        r'subprocess\.run\(.*pip.*install'
    ]
    
    with open(file_path, 'r') as f:
        content = f.read()
        for pattern in patterns:
            if re.search(pattern, content):
                violations.append(f"Internet call detected: {pattern}")
    
    return violations

def check_file_paths(file_path: Path) -> List[str]:
    """Check for hard-coded paths"""
    violations = []
    patterns = [
        r'https?://',
        r'/tmp/',
        r'/home/',
        r'C:\\',
        r'MODEL_DIR\s*=\s*["\']/[^/]'  # Absolute paths
    ]
    
    with open(file_path, 'r') as f:
        content = f.read()
        for pattern in patterns:
            if re.search(pattern, content):
                violations.append(f"Hard-coded path detected: {pattern}")
    
    return violations

def check_all(directory: Path = Path('.')) -> Dict[str, List[str]]:
    """Check all Python files in directory"""
    results = {
        'imports': [],
        'internet': [],
        'paths': []
    }
    
    for py_file in directory.rglob('*.py'):
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        results['imports'].extend(check_imports(py_file))
        results['internet'].extend(check_internet_calls(py_file))
        results['paths'].extend(check_file_paths(py_file))
    
    return results

if __name__ == '__main__':
    import sys
    results = check_all(Path('.'))
    
    total_violations = sum(len(v) for v in results.values())
    
    if total_violations > 0:
        print("❌ Compliance check FAILED")
        for category, violations in results.items():
            if violations:
                print(f"\n{category.upper()}:")
                for v in violations:
                    print(f"  - {v}")
        sys.exit(1)
    else:
        print("✅ Compliance check PASSED")
        sys.exit(0)
```

### 3. Create Git Pre-commit Hook

**File:** `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Pre-commit hook for Kaggle compliance

echo "🔍 Checking Kaggle compliance..."

python -m src.utils.compliance --check-all

if [ $? -ne 0 ]; then
    echo "❌ Compliance check failed! Commit blocked."
    echo "Fix violations or use --no-verify to skip (not recommended)"
    exit 1
fi

echo "✅ Compliance check passed!"
exit 0
```

**Make executable:**
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📚 Additional Resources

- **Kaggle Competition Rules:** See `Kaggle_deliverable_cnp.md`
- **PRD:** See `kaggle_pipeline_prd.md` (in d:\Gauntlet2\hv-ecg\)
- **Sprint Plan:** See `sprint_260121_02.md`

---

## 🆘 Getting Help

**If unsure about a change:**
1. Check this guide first
2. Review `.cursorrules` file
3. Run compliance checker
4. Ask: "Will this work offline in Kaggle?"

**Remember:** When in doubt, ASK. It's better to be cautious than break Kaggle submission.

---

**Last Updated:** January 21, 2026  
**Maintained By:** Development Team
