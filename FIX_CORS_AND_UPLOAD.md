# Fix CORS + Upload Images to Gallery

## 🚨 Two Issues Found:

1. **CORS not configured** - Blocking image access
2. **Storage is empty** - No images to display

---

## ✅ Step 1: Fix CORS (Use Correct Bucket Name)

Your Firebase Console shows: **`gs://hv-ecg.firebasestorage.app`**

### Run in PowerShell (as Administrator):

```powershell
# Set project
gcloud config set project hv-ecg

# Set CORS using the bucket name from your Firebase Console
gsutil cors set firebase-storage-cors.json gs://hv-ecg.firebasestorage.app
```

**If that fails, try the legacy name:**
```powershell
gsutil cors set firebase-storage-cors.json gs://hv-ecg.appspot.com
```

### Verify CORS:
```powershell
gsutil cors get gs://hv-ecg.firebasestorage.app
```

---

## ✅ Step 2: Upload Images to Storage

### Option A: Via Website (Recommended)

1. Go to: **https://hv-ecg.web.app/index.html**
2. Click: **"Choose Files"** or drag & drop ECG images
3. Click: **"Upload"**
4. Images will be stored in `ecg_images/` folder

### Option B: Via Firebase Console

1. Go to: **https://console.firebase.google.com/project/hv-ecg/storage**
2. Click: **"Upload file"** button
3. Create folder: **`ecg_images`** (if it doesn't exist)
4. Upload your ECG images

### Option C: Via gsutil (Command Line)

```powershell
# Upload a single image
gsutil cp "path/to/image.png" gs://hv-ecg.firebasestorage.app/ecg_images/

# Upload multiple images
gsutil -m cp "path/to/images/*.png" gs://hv-ecg.firebasestorage.app/ecg_images/
```

---

## ✅ Step 3: Test Gallery

1. **Refresh:** https://hv-ecg.web.app/gallery.html
2. **Check console:** Should see "Loaded X images" (no CORS errors)
3. **Images should appear** in the gallery grid

---

## 🔍 Verify Everything Works

### Check Storage via Firebase Console:
1. Go to: **https://console.firebase.google.com/project/hv-ecg/storage**
2. You should see:
   - Folder: **`ecg_images/`**
   - Files: Your uploaded images

### Check via gsutil:
```powershell
gsutil ls gs://hv-ecg.firebasestorage.app/ecg_images/
```

Should list your image files.

---

## ⚠️ If Gallery Still Empty After Upload:

### Check Firebase Storage Rules:

1. Go to: **Firebase Console** → **Storage** → **Rules** tab
2. Make sure rules allow reading:
   ```javascript
   match /ecg_images/{allPaths=**} {
     allow read: if true;  // Public read for gallery
     allow write: if request.auth != null;
   }
   ```

### Check Browser Console:

Open DevTools (F12) and check for:
- ✅ "Loaded X images" message
- ❌ Any CORS errors
- ❌ Any authentication errors

---

## 📋 Quick Checklist:

- [ ] Set CORS: `gsutil cors set firebase-storage-cors.json gs://hv-ecg.firebasestorage.app`
- [ ] Upload images via website or Firebase Console
- [ ] Verify images appear in Firebase Console Storage
- [ ] Refresh gallery page
- [ ] Check browser console for errors
- [ ] Images should now display!

---

**Once CORS is fixed AND images are uploaded, the gallery will work!** 🚀
