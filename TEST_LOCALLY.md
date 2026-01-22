# Test Backend Locally - Quick Guide

## Option 1: Use Firebase Emulators (Recommended for Testing)

### Step 1: Install Firebase Tools (if not already installed)
```powershell
npm install -g firebase-tools
```

### Step 2: Start Emulators
```powershell
firebase emulators:start
```

This starts:
- Functions emulator (for testing functions locally)
- Firestore emulator (uses your real Firestore data)
- Hosting emulator (serves your web app)

### Step 3: Open Testing Interface
Once emulators start, you'll see:
```
✔  functions[listGCSImages]: http function initialized
✔  functions[getGCSImageUrl]: http function initialized  
✔  functions[processGCSImage]: http function initialized
✔  Hosting: http://localhost:5000
```

Open: **http://localhost:5000/digitization_test.html**

---

## Option 2: Deploy to Firebase (Production)

### Fix Deployment Issue

The error suggests functions might not be properly exported. Let's verify:

```powershell
# Check if functions are exported correctly
cd functions
node -e "const f = require('./index.js'); console.log(Object.keys(f).filter(k => k.includes('GCS')))"
```

### Deploy All Functions
```powershell
# Deploy all functions (not just specific ones)
firebase deploy --only functions
```

### Then Deploy Hosting
```powershell
firebase deploy --only hosting
```

---

## Option 3: Test Functions Directly (Quick Test)

You can test functions using Firebase console or curl:

### Test listGCSImages
```powershell
# After deploying, test via Firebase console
# Or use curl if you have the function URL
```

---

## 🚀 Quick Start: Test Locally Now

**Easiest way to test right now:**

1. **Start emulators:**
   ```powershell
   firebase emulators:start
   ```

2. **Open browser:**
   - Go to: `http://localhost:5000/digitization_test.html`
   - Or: `http://localhost:5000/training_viewer.html`

3. **Click "Load Images from GCS"**

4. **Select images and test!**

---

## 📋 What Each Page Does

### `digitization_test.html` (New Testing Page)
- ✅ Loads images automatically
- ✅ Select multiple images
- ✅ Batch process
- ✅ View aggregate results

### `training_viewer.html` (Updated Viewer)
- ✅ Load images from GCS
- ✅ Browse and filter
- ✅ Test individual images
- ✅ Compare with ground truth

---

## 🔧 Troubleshooting

### "Functions not found" error
- ✅ Make sure you're in project root
- ✅ Check `functions/index.js` has the exports
- ✅ Try: `firebase deploy --only functions` (deploy all)

### "Firestore permission denied"
- ✅ Make sure you're logged in: `firebase login`
- ✅ Check Firestore rules allow reads

### "GCS access denied"
- ✅ Make sure service account has Storage Admin role
- ✅ Check bucket permissions

---

## ✅ Recommended: Start with Emulators

**Best for testing:**
```powershell
firebase emulators:start
```

Then open: `http://localhost:5000/digitization_test.html`

This lets you test without deploying!
