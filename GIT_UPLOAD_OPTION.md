# Upload via Git (Alternative Method)

If the file upload isn't working, using Git is a reliable alternative.

## Option 1: Quick Check - File Might Be in Home Directory

First, let's check if the file is already there. In Cloud Shell terminal:

```bash
cd ~
ls -la *.zip
ls -la functions*
```

If you see the zip file, we can extract it directly.

## Option 2: Use Git (Recommended if upload failed)

### Step 1: Create a Git Repository (Local Machine)

On your **local machine** (PowerShell):

```powershell
cd "C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg"
git init
git add functions_python
git commit -m "Add functions_python for Cloud Run deployment"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (name it `ecg-functions-python` or similar)
3. **Don't** initialize with README
4. Copy the repository URL

### Step 3: Push to GitHub (Local Machine)

```powershell
git remote add origin https://github.com/YOUR_USERNAME/ecg-functions-python.git
git branch -M main
git push -u origin main
```

### Step 4: Clone in Cloud Shell

In **Cloud Shell terminal**:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/ecg-functions-python.git
cd ecg-functions-python
ls -la
```

You should see the `functions_python` folder!

### Step 5: Build and Deploy

```bash
cd functions_python
gcloud config set project hv-ecg
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```

## Option 3: Simpler - Just Upload the Folder Directly

Actually, you can upload the entire `functions_python` folder (not zipped) via File menu:

1. In Cloud Shell Editor: **File** → **Upload...**
2. Select the entire `functions_python` folder (not the zip)
3. This might work better than the zip file

## Recommendation

Try **Option 1** first (check if file is already there), then **Option 3** (upload folder directly). Git is reliable but takes more steps.
