# 🔧 Quick Setup - Run These Commands

## ✅ Step 1: Install Packages (Done!)
`google-cloud-storage` is now installed!

## 🔑 Step 2: Set Authentication

**In your PowerShell terminal (the one you're using), run:**

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\service-account-key.json"
```

**Or run the script I created:**

```powershell
.\set_gcs_auth.ps1
```

**Or install it permanently (recommended):**

```powershell
.\install_gcs_auth_profile.ps1
```

## ✅ Step 3: Test Authentication

```powershell
python test_gcs_auth.py
```

**Expected output:**
```
✓ Authentication successful!
✓ Connected to project: hv-ecg
```

## 🚀 Step 4: Create Buckets

Once authentication works:

```powershell
python scripts/create_multiple_gcs_buckets.py
```

---

## 💡 Why This Happened

The environment variable you set in your terminal doesn't carry over to this script's shell session. You need to set it in **this PowerShell window** (or install it permanently to your profile).
