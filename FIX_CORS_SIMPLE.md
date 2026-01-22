# Fix Firebase Storage CORS - Simple Method

## 🚨 The Problem

CORS errors prevent the gallery from loading images from Firebase Storage.

---

## ✅ Quick Fix (3 Commands)

### Step 1: Install Google Cloud SDK

**If not installed:**
```powershell
winget install Google.CloudSDK
```

**Or download from:** https://cloud.google.com/sdk/docs/install

### Step 2: Authenticate

```powershell
gcloud auth login
```

This opens a browser - sign in with your Google account.

### Step 3: Set CORS

```powershell
gsutil cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

---

## ✅ Verify It Worked

```powershell
gsutil cors get gs://hv-ecg.appspot.com
```

Should show the CORS configuration.

---

## 🧪 Test

1. **Refresh gallery:** https://hv-ecg.web.app/gallery.html
2. **Check console:** No more CORS errors
3. **Images should load**

---

## ⚠️ If gsutil Not Found

**Check installation:**
```powershell
where.exe gsutil
```

**If not found, add to PATH:**
- Google Cloud SDK installs to: `C:\Users\<YourUser>\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`
- Add this to your PATH environment variable

**Or use full path:**
```powershell
& "C:\Users\$env:USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gsutil.cmd" cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

---

## 📋 Manual Method (If Script Fails)

**Option 1: Google Cloud Console**
1. Go to: https://console.cloud.google.com/storage/browser
2. Click: `hv-ecg.appspot.com` bucket
3. Go to: **Permissions** tab → **CORS** section
4. Click: **Edit CORS configuration**
5. Paste content from `firebase-storage-cors.json`
6. Click: **Save**

**Option 2: Use Python Script**
```powershell
python scripts/configure_gcs_cors.py
```
(But this is for GCS buckets, not Firebase Storage)

---

**The simplest fix is the 3 commands above!** 🚀
