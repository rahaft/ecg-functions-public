# Fix Authentication Error: auth/admin-restricted-operation

This error occurs when your API key has restrictions that prevent anonymous authentication.

## Step-by-Step Fix

### Step 1: Fix API Key Restrictions in Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select project: **hv-ecg**

2. **Navigate to API Key Settings**
   - Click **APIs & Services** in the left menu
   - Click **Credentials**
   - Find your API key: `AIzaSyAsIWxy1gTV1_e9ZXZnaplcOWqU9PwL_Uc`
   - Click on the API key name to edit it

3. **Fix Application Restrictions**
   - Under **"Application restrictions"**, you have two options:
   
   **Option A (Recommended for Development):**
   - Select **"None"** (no restrictions)
   - Click **Save**
   
   **Option B (For Production):**
   - Select **"HTTP referrers (web sites)"**
   - Click **"Add an item"** and add these domains:
     ```
     https://hv-ecg.web.app/*
     https://hv-ecg.firebaseapp.com/*
     http://localhost:*
     ```
   - Click **Save**

4. **Fix API Restrictions**
   - Under **"API restrictions"**, you have two options:
   
   **Option A (Recommended):**
   - Select **"Don't restrict key"**
   - Click **Save**
   
   **Option B:**
   - Select **"Restrict key"**
   - Make sure these APIs are enabled:
     - ✅ Identity Toolkit API
     - ✅ Firebase Installations API
     - ✅ Firebase Remote Config API
   - Click **Save**

5. **Wait 1-2 minutes** for changes to propagate

### Step 2: Verify Authorized Domains in Firebase Console

1. **Go to Firebase Console**
   - Visit: https://console.firebase.google.com/project/hv-ecg/authentication/settings
   - Or: Firebase Console > Authentication > Settings

2. **Check Authorized Domains**
   - Scroll to **"Authorized domains"** section
   - Make sure these domains are listed:
     - ✅ `hv-ecg.web.app`
     - ✅ `hv-ecg.firebaseapp.com`
     - ✅ `localhost` (for local development)
   
   - If any are missing, click **"Add domain"** and add them

3. **Verify Anonymous Authentication is Enabled**
   - Go to: **Authentication > Sign-in method**
   - Find **"Anonymous"** in the list
   - Make sure it's **Enabled** (toggle should be ON)
   - If not enabled, click on it and toggle it ON, then click **Save**

### Step 3: Enable Required APIs

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/apis/library?project=hv-ecg

2. **Enable Required APIs**
   - Search for and enable these APIs if not already enabled:
     - ✅ **Identity Toolkit API**
     - ✅ **Firebase Installations API**
     - ✅ **Firebase Remote Config API**

### Step 4: Test

1. **Clear browser cache** (or use incognito mode)
2. **Visit**: https://hv-ecg.web.app
3. **Click "Sign In"**
4. **Check browser console** for any errors

## Quick Links

- **Google Cloud Console**: https://console.cloud.google.com/apis/credentials?project=hv-ecg
- **Firebase Console Auth Settings**: https://console.firebase.google.com/project/hv-ecg/authentication/settings
- **Firebase Console Sign-in Methods**: https://console.firebase.google.com/project/hv-ecg/authentication/providers

## Common Issues

### Issue: "API key restrictions" error persists after changes
- **Solution**: Wait 2-5 minutes for changes to propagate, then clear browser cache

### Issue: Can't find the API key in Google Cloud Console
- **Solution**: Make sure you're in the correct project (hv-ecg). The API key starts with `AIzaSy...`

### Issue: "Identity Toolkit API" is not enabled
- **Solution**: Go to APIs & Services > Library, search for "Identity Toolkit API", and click Enable

## Still Having Issues?

If the error persists after following all steps:
1. Check the browser console for the exact error message
2. Verify you're using the correct API key in `public/index.html`
3. Try creating a new API key without restrictions as a test
4. Check Firebase project billing status (some features require billing enabled)
