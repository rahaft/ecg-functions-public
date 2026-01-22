# How to Find Your Firebase PROJECT_NUMBER

## Method 1: Firebase Console (Easiest)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project **hv-ecg**
3. Click the **⚙️ gear icon** next to "Project Overview"
4. Click **Project Settings**
5. Scroll down to **Your project** section
6. You'll see:
   - **Project ID**: `hv-ecg`
   - **Project number**: `123456789012` (this is what you need!)

## Method 2: Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project **hv-ecg** from the dropdown
3. Click the **⚙️ gear icon** in the top right
4. Click **Project Settings**
5. The **Project number** is displayed at the top

## Method 3: Firebase CLI

Run this command in your terminal:

```powershell
firebase projects:list
```

This will show all your projects with their numbers.

## Method 4: From Firebase Config

If you have the Firebase config, the project number might be in the storage bucket name or other settings, but the methods above are more reliable.

---

## Once You Have the PROJECT_NUMBER

Your service account email will be:
```
PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

For example, if your project number is `123456789012`, the service account would be:
```
123456789012-compute@developer.gserviceaccount.com
```
