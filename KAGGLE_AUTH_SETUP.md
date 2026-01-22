# Kaggle API Authentication Setup

## 🔑 Why This Happened

The transfer script found **0 images** because Kaggle API authentication isn't configured. The error `401 Unauthorized` means the script can't connect to Kaggle.

## ✅ Quick Setup (5 minutes)

### Step 1: Get Kaggle API Token

1. **Go to:** https://www.kaggle.com/account
2. **Scroll down** to "API" section
3. **Click "Create New Token"**
4. **File downloads:** `kaggle.json` (contains username and API key)

### Step 2: Place the File

**Move the `kaggle.json` file to:**
```
C:\Users\Rosi\.kaggle\kaggle.json
```

**To create the directory and move the file:**

**PowerShell:**
```powershell
# Create directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.kaggle"

# Move the file (adjust path if different)
Move-Item -Path "$env:USERPROFILE\Downloads\kaggle.json" -Destination "$env:USERPROFILE\.kaggle\kaggle.json"

# Set permissions (Windows - make it private)
icacls "$env:USERPROFILE\.kaggle\kaggle.json" /inheritance:r /grant:r "$env:USERNAME:(R)"
```

**Or manually:**
1. Create folder: `C:\Users\Rosi\.kaggle\`
2. Copy `kaggle.json` to that folder

### Step 3: Verify Setup

**Test the Kaggle API:**
```powershell
python test_kaggle_list.py
```

**Expected output:**
```
Fetching files from competition: physionet-ecg-image-digitization
Found X total files
Found Y image files
```

### Step 4: Run Transfer Again

Once authentication works:
```powershell
python scripts/kaggle_to_gcs_transfer.py
```

---

## 📋 Alternative: Environment Variables

If you prefer to use environment variables instead of a file:

```powershell
# Set Kaggle credentials as environment variables
$env:KAGGLE_USERNAME = "your_kaggle_username"
$env:KAGGLE_KEY = "your_api_key_here"
```

**Then run:**
```powershell
python scripts/kaggle_to_gcs_transfer.py
```

---

## 🔒 Security Note

⚠️ **Never commit `kaggle.json` to Git!**

Make sure `.kaggle/` is in your `.gitignore`:

```
.kaggle/
*.json
!firebase.json
!package.json
!tsconfig.json
```

---

## 🆘 Troubleshooting

### "File not found" error
- ✅ Check the path: `C:\Users\Rosi\.kaggle\kaggle.json`
- ✅ Make sure the file exists
- ✅ Verify the `.kaggle` folder exists

### "401 Unauthorized" error
- ✅ Check your Kaggle username is correct
- ✅ Verify the API key is valid (create a new token if needed)
- ✅ Make sure the file format is correct JSON

### "Permission denied" error (Linux/Mac)
- ✅ Set file permissions: `chmod 600 ~/.kaggle/kaggle.json`

---

## ✅ After Setup

Once `kaggle.json` is in place:

1. ✅ Test: `python test_kaggle_list.py`
2. ✅ Run transfer: `python scripts/kaggle_to_gcs_transfer.py`

The script should now find and transfer all images!
