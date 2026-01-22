# Quick Start: Test Backend Locally

## 🚀 Fastest Way to Test (2 minutes)

### Step 1: Start Firebase Emulators

```powershell
firebase emulators:start
```

**Wait for:**
```
✔  All emulators ready!
✔  functions[listGCSImages]: http function initialized
✔  functions[getGCSImageUrl]: http function initialized
✔  functions[processGCSImage]: http function initialized
✔  Hosting: http://localhost:5000
```

### Step 2: Open Testing Page

**In your browser, go to:**
- **http://localhost:5000/digitization_test.html**

**OR**

- **http://localhost:5000/training_viewer.html**

### Step 3: Load Images

1. **Click:** "Load Images from GCS" (or images load automatically on test page)
2. **Wait** for images to appear
3. **Click** images to select them
4. **Click:** "Test Selected" or "Test Digitization"
5. **View results!**

---

## 📊 What You'll See

### Digitization Test Page:
- Grid of image thumbnails
- Click to select multiple images
- "Test Selected" button processes all selected
- Results panel shows:
  - Images processed
  - Average SNR
  - Total leads detected
  - Signal visualization

### Training Viewer:
- Image cards with metadata
- "Test Digitization" button on each card
- Comparison view with metrics
- Ground truth comparison (when available)

---

## 🔧 If Emulators Don't Start

**Check Firebase CLI:**
```powershell
firebase --version
```

**If not installed:**
```powershell
npm install -g firebase-tools
firebase login
```

**Then try again:**
```powershell
firebase emulators:start
```

---

## ✅ That's It!

Once emulators are running, you can:
- ✅ View all 8,795 images
- ✅ Test digitization on any image
- ✅ See processing results
- ✅ View quality metrics

**No deployment needed for local testing!**
