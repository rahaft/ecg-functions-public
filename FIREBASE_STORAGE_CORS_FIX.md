# Fix Firebase Storage CORS - Correct Method

## 🚨 The Issue

Firebase Storage buckets (like `hv-ecg.appspot.com`) are **not visible** in Google Cloud Storage Console. They must be accessed through **Firebase Console** or configured via `gsutil` with the correct project.

---

## ✅ Method 1: Firebase Console (Easiest - No Admin Needed)

### Step 1: Access Firebase Storage

1. Go to: **https://console.firebase.google.com/**
2. Select project: **hv-ecg**
3. Click: **Storage** (left sidebar)
4. You should see your bucket and files

### Step 2: Set CORS via gsutil (with correct project)

**Important:** You must set the GCP project first!

```powershell
# Set the correct project
gcloud config set project hv-ecg

# Verify project
gcloud config get-value project

# Now set CORS (run PowerShell as Administrator if needed)
gsutil cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

### Step 3: Verify CORS

```powershell
gsutil cors get gs://hv-ecg.appspot.com
```

---

## ✅ Method 2: Use gsutil with Project Context

The bucket exists, but you need to be in the correct project:

```powershell
# 1. Set project
gcloud config set project hv-ecg

# 2. Verify you can see the bucket
gsutil ls gs://hv-ecg.appspot.com

# 3. If that works, set CORS (run as Admin if permission error)
gsutil cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

---

## ✅ Method 3: Google Cloud Console (Alternative)

If you need to use GCS Console:

1. **Make sure you're in the correct project:**
   - Top bar should show: **Project: hv-ecg**
   - If not, click the project dropdown and select **hv-ecg**

2. **Access Storage:**
   - Go to: **https://console.cloud.google.com/storage/browser?project=hv-ecg**
   - Or: **Storage** → **Browser** (left sidebar)

3. **Find the bucket:**
   - Look for: `hv-ecg.appspot.com` or `hv-ecg.firebasestorage.app`
   - Firebase Storage buckets may have different names in GCS Console

4. **Set CORS:**
   - Click the bucket
   - Go to: **Permissions** tab → **CORS** section
   - Click: **Edit CORS configuration**
   - Paste the JSON from `firebase-storage-cors.json`
   - Click: **Save**

---

## 🔍 Verify Bucket Exists

### Check via Firebase Console:

1. Go to: **https://console.firebase.google.com/project/hv-ecg/storage**
2. You should see files in the `ecg_images/` folder
3. If you see files, the bucket exists!

### Check via gsutil:

```powershell
# Set project first
gcloud config set project hv-ecg

# List bucket contents
gsutil ls gs://hv-ecg.appspot.com/ecg_images/
```

If this works, the bucket exists and you can set CORS.

---

## ⚠️ If "Bucket not found" persists:

### Option A: Bucket might have a different name

Firebase Storage buckets can be:
- `hv-ecg.appspot.com` (default)
- `hv-ecg.firebasestorage.app` (newer format)

**Check in Firebase Console:**
1. Go to: **Storage** → **Files** tab
2. Look at the URL or bucket name shown
3. Use that exact name in `gsutil` commands

### Option B: Create the bucket (if it doesn't exist)

```powershell
# Set project
gcloud config set project hv-ecg

# Create bucket (if needed)
gsutil mb -p hv-ecg -c STANDARD -l us-central1 gs://hv-ecg.appspot.com
```

**But wait!** If you're using Firebase Storage, the bucket should be created automatically when you enable Storage in Firebase Console.

---

## 🎯 Recommended Steps (Right Now):

### Step 1: Use the Correct Bucket Name

**Your Firebase Console shows:** `gs://hv-ecg.firebasestorage.app`

**Your code uses:** `hv-ecg.appspot.com`

Both names work, but use the one from your console for CORS:

```powershell
# Set project
gcloud config set project hv-ecg

# Set CORS using the bucket name from Firebase Console
gsutil cors set firebase-storage-cors.json gs://hv-ecg.firebasestorage.app
```

**OR** if that doesn't work, try the legacy name:
```powershell
gsutil cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

### Step 2: Check if Storage is Empty

**If Firebase Console shows "There are no files here yet":**
- The gallery will be empty even after fixing CORS
- You need to upload images first via the upload page: https://hv-ecg.web.app/index.html
- Or upload via Firebase Console: Click "Upload file" button

### Step 3: Verify CORS Applied

```powershell
gsutil cors get gs://hv-ecg.firebasestorage.app
```

### Step 4: Test Gallery

1. **Upload some test images** via: https://hv-ecg.web.app/index.html
2. **Refresh gallery:** https://hv-ecg.web.app/gallery.html
3. **Check console:** No CORS errors

---

## 📋 CORS JSON (for reference):

```json
[
  {
    "origin": [
      "https://hv-ecg.web.app",
      "https://hv-ecg.firebaseapp.com",
      "http://localhost:5000",
      "http://localhost:8000"
    ],
    "method": ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"],
    "responseHeader": [
      "Content-Type",
      "Authorization",
      "x-goog-resumable",
      "x-goog-upload-command",
      "x-goog-upload-protocol",
      "x-goog-upload-status"
    ],
    "maxAgeSeconds": 3600
  }
]
```

---

**The key is: Firebase Storage buckets must be accessed through Firebase Console or with the correct `gcloud` project context!** 🚀
