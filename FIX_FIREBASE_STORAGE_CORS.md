# Fix Firebase Storage CORS Error

## 🚨 Problem

**Error:**
```
Access to XMLHttpRequest at 'https://firebasestorage.googleapis.com/...' 
from origin 'https://hv-ecg.web.app' has been blocked by CORS policy
```

**Cause:** Firebase Storage bucket doesn't have CORS configured to allow requests from `https://hv-ecg.web.app`

---

## ✅ Solution: Configure CORS via gsutil

Firebase Storage uses Google Cloud Storage under the hood. We need to configure CORS using `gsutil`.

### Step 1: Create CORS Configuration File

Create `firebase-storage-cors.json`:

```json
[
  {
    "origin": ["https://hv-ecg.web.app", "https://hv-ecg.firebaseapp.com"],
    "method": ["GET", "HEAD", "POST", "PUT", "DELETE"],
    "responseHeader": ["Content-Type", "Authorization", "x-goog-resumable"],
    "maxAgeSeconds": 3600
  }
]
```

### Step 2: Apply CORS Configuration

```powershell
# Install gsutil if not installed
# gsutil comes with Google Cloud SDK

# Set CORS configuration
gsutil cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

### Step 3: Verify CORS is Set

```powershell
gsutil cors get gs://hv-ecg.appspot.com
```

---

## 🔧 Alternative: Use gcloud CLI

If `gsutil` is not available, use `gcloud`:

```powershell
# Authenticate
gcloud auth login

# Set CORS (requires creating JSON file first)
gcloud storage buckets update gs://hv-ecg.appspot.com --cors-file=firebase-storage-cors.json
```

---

## 📝 Quick Fix Script

I'll create a PowerShell script to automate this:
