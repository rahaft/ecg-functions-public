# Kaggle API Token Setup (New Method)

## ✅ What Changed

Kaggle now uses **API tokens** (like `KGAT_...`) instead of JSON files. This is simpler!

## 🚀 Quick Setup

### Option 1: Use the Script (Easiest)

I've created a script that sets your credentials:

```powershell
.\set_kaggle_auth.ps1
```

This sets:
- `KAGGLE_USERNAME` = `raconcilio`
- `KAGGLE_API_TOKEN` = `KGAT_c70783487531b81b83b96755edfcace6`

### Option 2: Set Environment Variables Manually

**In PowerShell:**
```powershell
$env:KAGGLE_USERNAME = "raconcilio"
$env:KAGGLE_API_TOKEN = "KGAT_c70783487531b81b83b96755edfcace6"
```

**Note:** These only last for the current PowerShell session. Use the script or Option 3 for permanent setup.

### Option 3: Add to PowerShell Profile (Permanent)

**Edit your PowerShell profile:**
```powershell
notepad $PROFILE
```

**Add these lines:**
```powershell
# Kaggle API Authentication
$env:KAGGLE_USERNAME = "raconcilio"
$env:KAGGLE_API_TOKEN = "KGAT_c70783487531b81b83b96755edfcace6"
```

**Save and close.** Now authentication is set every time you open PowerShell!

**To apply immediately:**
```powershell
. $PROFILE
```

## ✅ Test Authentication

**Run:**
```powershell
python test_kaggle_list.py
```

**Expected output:**
```
Fetching files from competition: physionet-ecg-image-digitization
Found X total files
Found Y image files
```

## 🚀 Run Transfer

Once authentication is set:

```powershell
# Set credentials (if not in profile)
.\set_kaggle_auth.ps1

# Run transfer
python scripts/kaggle_to_gcs_transfer.py
```

## 🔒 Security Note

⚠️ **Never commit your API token to Git!**

The token is in `set_kaggle_auth.ps1` - this is okay for local use, but:
- Don't share this file publicly
- If using Git, consider using environment variables instead
- Or use a `.env` file (not committed)

## 📋 Combined Setup

For complete setup (both Google Cloud and Kaggle):

```powershell
# Set Google Cloud authentication
.\set_gcs_auth.ps1

# Set Kaggle authentication
.\set_kaggle_auth.ps1

# Test everything
python test_gcs_auth.py
python test_kaggle_list.py

# Run transfer
python scripts/kaggle_to_gcs_transfer.py
```

## 🆘 Troubleshooting

### "401 Unauthorized" error
- ✅ Check `KAGGLE_USERNAME` is set correctly
- ✅ Verify `KAGGLE_API_TOKEN` is set correctly
- ✅ Make sure token starts with `KGAT_`

### "Environment variable not set"
- ✅ Run `.\set_kaggle_auth.ps1` first
- ✅ Or set environment variables manually

### Token expires or doesn't work
- ✅ Generate a new token from: https://www.kaggle.com/account
- ✅ Update `set_kaggle_auth.ps1` with new token
