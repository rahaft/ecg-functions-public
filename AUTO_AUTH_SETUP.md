# Automatic Authentication Setup

I've created scripts to automatically set Google Cloud authentication so you don't have to remember!

## 🎯 Quick Setup (Choose One Option)

### Option 1: Add to PowerShell Profile (Recommended - Permanent)

**This sets authentication automatically every time you open PowerShell:**

```powershell
# Run this once - it will add authentication to your PowerShell profile
python scripts/install_gcs_auth_profile.ps1

# Or if that doesn't work:
.\install_gcs_auth_profile.ps1
```

**After running this:**
- ✅ Authentication is set automatically every time you open PowerShell
- ✅ No need to remember anything!
- ✅ Works for all new PowerShell windows

**To apply immediately (without closing/reopening PowerShell):**
```powershell
. $PROFILE
```

---

### Option 2: Run Script Before Running Commands

**If you don't want it automatic, just run this before any GCS commands:**

**PowerShell:**
```powershell
.\set_gcs_auth.ps1
```

**Command Prompt (CMD):**
```cmd
set_gcs_auth.bat
```

**Then run your scripts:**
```powershell
python scripts/create_multiple_gcs_buckets.py
python scripts/kaggle_to_gcs_transfer.py
```

---

## 📁 Scripts Created

1. **`set_gcs_auth.ps1`** - PowerShell script to set authentication (run manually)
2. **`set_gcs_auth.bat`** - Batch file to set authentication (for CMD)
3. **`install_gcs_auth_profile.ps1`** - Installs authentication to PowerShell profile (permanent)

---

## 🚀 Recommended: Install to Profile

**Run this once:**

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
.\install_gcs_auth_profile.ps1
```

**That's it!** Now every time you open PowerShell, authentication will be set automatically.

**Verify it works:**
```powershell
# Close and reopen PowerShell, then:
python -c "from google.cloud import storage; client = storage.Client(project='hv-ecg'); print('✓ Authentication successful!')"
```

---

## 🔧 Manual Script Usage

If you prefer to run it manually each time:

```powershell
# Before running any GCS scripts:
.\set_gcs_auth.ps1

# Then run your scripts:
python scripts/create_multiple_gcs_buckets.py
```

---

## 📝 What the Profile Script Does

The `install_gcs_auth_profile.ps1` script:

1. ✅ Checks if `service-account-key.json` exists
2. ✅ Finds your PowerShell profile location
3. ✅ Adds a line to set `GOOGLE_APPLICATION_CREDENTIALS` automatically
4. ✅ Makes it happen every time you open PowerShell

**The line it adds:**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"
```

---

## 🆘 Troubleshooting

### "Script execution is disabled"
```powershell
# Run this in PowerShell as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Profile not found"
The script will create it automatically!

### "File not found"
Make sure `service-account-key.json` is in your project root directory.

---

## ✅ After Setup

Once installed, you can:

1. ✅ Open PowerShell
2. ✅ Authentication is set automatically
3. ✅ Run scripts directly:
   ```powershell
   python scripts/create_multiple_gcs_buckets.py
   ```

No need to remember anything!
