# Quick Guide: Import Manifest to Firestore

## ✅ You Have:
- Manifest file: `image_manifest_gcs.json` (8,795 images)

## 🔑 You Need:
Firebase Admin credentials (`serviceAccountKey.json`)

## 🚀 Two Ways to Get It:

### Method 1: Firebase CLI (Easiest)
```powershell
npm install -g firebase-tools
firebase login
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

### Method 2: Download Service Account Key
1. Go to: https://console.firebase.google.com/project/hv-ecg/settings/serviceaccounts/adminsdk
2. Click "Generate new private key"
3. Save as `serviceAccountKey.json` in project root
4. Run: `python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json`

## 📊 After Import:

Your Firestore `kaggle_images` collection will have:
- ✅ 8,795 image documents
- ✅ GCS bucket/path info
- ✅ Train/test labels
- ✅ Folder structure

Then we can build the viewer and testing interface!
