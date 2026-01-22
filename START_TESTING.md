# Start Testing - Quick Guide

## ✅ Firebase Emulators Starting

The emulators are starting in the background. Once you see:
```
✔  All emulators ready!
✔  Hosting: http://localhost:5000
```

## 🚀 Open Testing Pages

### Option 1: Dedicated Testing Page (Recommended)
**Go to:** http://localhost:5000/digitization_test.html

**Features:**
- ✅ Images load automatically
- ✅ Select multiple images
- ✅ Batch process
- ✅ View aggregate results

### Option 2: Training Viewer
**Go to:** http://localhost:5000/training_viewer.html

**Features:**
- ✅ Browse all images
- ✅ Filter by train/test
- ✅ Test individual images
- ✅ Compare with ground truth

## 📋 How to Test

### On Digitization Test Page:
1. **Images load automatically** (first 50)
2. **Click images** to select them (they highlight)
3. **Click "Test Selected"** button
4. **View results** in the results panel

### On Training Viewer:
1. **Click "Load Images from GCS"**
2. **Browse images** in the grid
3. **Click "Test Digitization"** on any image card
4. **View results** in comparison view

## 🔍 What You'll See

**Results include:**
- ✅ SNR (Signal-to-Noise Ratio)
- ✅ Grid quality score
- ✅ Number of leads detected
- ✅ Signal visualization (on test page)

## ⚠️ If Functions Don't Work

The functions use your **real Firestore data** (the 8,795 images you imported).

If you get errors:
1. ✅ Check emulator console for error messages
2. ✅ Make sure Firestore emulator is connected to real data
3. ✅ Verify `kaggle_images` collection has data

## 🎯 Next Steps After Testing

Once you verify it works locally:
1. **Deploy functions:**
   ```powershell
   firebase deploy --only functions
   ```

2. **Deploy hosting:**
   ```powershell
   firebase deploy --only hosting
   ```

3. **Access live:**
   - https://hv-ecg.web.app/digitization_test.html

---

**The emulators should be starting now. Check the terminal for the URL!**
