# Fixing Kaggle 401 Unauthorized Error

## ✅ What's Working

- ✅ `kaggle.json` file exists at `C:\Users\Rosi\.kaggle\kaggle.json`
- ✅ File format is correct JSON
- ✅ Username and token are present

## ❌ Current Issue

**401 Client Error: Unauthorized** - The Kaggle API is rejecting the authentication.

## 🔍 Common Causes & Solutions

### Solution 1: Accept Competition Terms (MOST LIKELY)

**This is required before downloading competition data!**

1. **Go to the competition page:**
   - https://www.kaggle.com/competitions/physionet-ecg-image-digitization

2. **Click "Join Competition"** (if not already joined)

3. **Accept the rules:**
   - Go to: https://www.kaggle.com/competitions/physionet-ecg-image-digitization/rules
   - Read the rules
   - Click **"I Understand and Accept"** button

4. **Test again:**
   ```powershell
   python test_kaggle_list.py
   ```

### Solution 2: Verify API Token is Valid

1. **Go to:** https://www.kaggle.com/account
2. **Scroll to "API" section**
3. **Check if token is active**
4. **If needed, create a new token:**
   - Click "Create New Token"
   - Copy the new token (starts with `KGAT_...`)
   - Update `kaggle.json`:
     ```powershell
     # Edit the token in the script
     # Or manually edit: C:\Users\Rosi\.kaggle\kaggle.json
     ```

### Solution 3: Check Token Format

**The token in `kaggle.json` should:**
- Start with `KGAT_` (not `kgat_` or other variants)
- Be the full token (no spaces or extra characters)
- Match exactly what's shown on Kaggle

**Verify:**
```powershell
# Check current token
python test_kaggle_json.py
```

### Solution 4: Use Environment Variables Instead

**If the JSON file isn't working, try environment variables:**

```powershell
# Set environment variables
$env:KAGGLE_USERNAME = "raconcilio"
$env:KAGGLE_KEY = "KGAT_c70783487531b81b83b96755edfcace6"

# Test
python test_kaggle_list.py
```

### Solution 5: Check Internet/Firewall

- Make sure you can access: https://www.kaggle.com
- Check if firewall/proxy is blocking `api.kaggle.com`
- Try from a different network if possible

## 📋 Step-by-Step Fix (Try in Order)

### Step 1: Accept Competition Terms
1. Visit: https://www.kaggle.com/competitions/physionet-ecg-image-digitization
2. Click "Join Competition" (if not joined)
3. Go to Rules: https://www.kaggle.com/competitions/physionet-ecg-image-digitization/rules
4. Click "I Understand and Accept"

### Step 2: Verify Token
1. Go to: https://www.kaggle.com/account
2. Check API token section
3. If token looks different or expired, create a new one

### Step 3: Update Token (if needed)

**If you got a new token, update it:**

```powershell
# Edit create_kaggle_json_simple.ps1 with new token
# Then run:
.\create_kaggle_json_simple.ps1
```

### Step 4: Test Again
```powershell
python test_kaggle_list.py
```

## ✅ Expected Success Output

```
Fetching files from competition: physionet-ecg-image-digitization
Found X total files
Found Y image files

First 10 image files:
  - train/image1.png (123456 bytes)
  - train/image2.png (234567 bytes)
  ...
```

## 🆘 Still Not Working?

If you've tried all of the above and still get 401:

1. **Double-check:**
   - ✅ Competition terms accepted?
   - ✅ Token is correct and active?
   - ✅ Username is correct?
   - ✅ File is at `C:\Users\Rosi\.kaggle\kaggle.json`?

2. **Try generating a new token:**
   - Sometimes tokens expire or get corrupted
   - Generate a fresh one from Kaggle

3. **Check Kaggle status:**
   - Sometimes Kaggle API has temporary issues
   - Check: https://status.kaggle.com/

## 📞 Next Steps After Fix

Once authentication works:

```powershell
# Test
python test_kaggle_list.py

# Run transfer
python scripts/kaggle_to_gcs_transfer.py
```
