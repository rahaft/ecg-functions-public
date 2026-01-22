# Google Cloud Authentication Guide

## What Password Is It Asking For?

The password prompt is for your **Google Cloud account** authentication. This is needed to:
- Build Docker images in Google Container Registry
- Deploy services to Cloud Run
- Access your Google Cloud project

## Solution: Authenticate with gcloud

### Option 1: Login with Browser (Easiest) ⭐

This will open a browser window for you to sign in:

```powershell
gcloud auth login
```

**Steps:**
1. Run the command above
2. A browser window will open
3. Sign in with your Google account (the one associated with the `hv-ecg` project)
4. Allow access
5. Return to terminal - you're now authenticated!

### Option 2: Use Application Default Credentials

If you've already authenticated before, you might just need to refresh:

```powershell
gcloud auth application-default login
```

### Option 3: Check Current Authentication

See who you're logged in as:

```powershell
gcloud auth list
```

### Option 4: If You Don't Have Access

If you don't have access to the Google Cloud account, you'll need to:
1. Get access from the project owner, OR
2. Use a service account key (if provided)

---

## Quick Fix: Re-authenticate and Continue

**Run these commands:**

```powershell
# 1. Authenticate (opens browser)
gcloud auth login

# 2. Set the project
gcloud config set project hv-ecg

# 3. Continue with deployment
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```

---

## Alternative: Skip Password Prompt

If you want to avoid the password prompt during the script, you can authenticate first:

```powershell
# Authenticate first
gcloud auth login

# Then run the deployment script
.\deploy_now.ps1
```

The script should then run without asking for a password.

---

## Troubleshooting

### "Permission Denied" Errors

If you get permission errors after authenticating:
- Make sure you're using the correct Google account
- Verify you have access to the `hv-ecg` project
- Check your role: `gcloud projects get-iam-policy hv-ecg`

### "Project Not Found"

If the project isn't found:
- Verify project ID: `gcloud projects list`
- Set correct project: `gcloud config set project hv-ecg`

---

*Authentication Guide - January 21, 2026*
