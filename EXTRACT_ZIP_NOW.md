# Extract the Zip File - Quick Steps

The zip file is uploaded but not in the current directory. Let's find and extract it.

## Step 1: Check Current Directory

In Cloud Shell terminal, run:

```bash
pwd
ls -la
```

## Step 2: Check Home Directory

The file might be in your home directory:

```bash
cd ~
ls -la functions_python.zip
```

## Step 3: If Found in Home, Move and Extract

```bash
# If the file is in ~, move it to ecg-service
mkdir -p ~/ecg-service
mv ~/functions_python.zip ~/ecg-service/
cd ~/ecg-service
unzip functions_python.zip
```

## Step 4: If File Menu Uploaded to a Different Location

Sometimes File menu uploads go to a specific location. Try:

```bash
# Check if it's in the editor's workspace
ls -la ~/.codeoss/
# Or check Downloads
ls -la ~/Downloads/
```

## Step 5: Alternative - Download from Editor

If the file is open in the editor:
1. Right-click on `functions_python.zip` in the file explorer (left sidebar)
2. Select "Download" to save it locally
3. Then re-upload it to the correct location

## Step 6: Once Extracted, Verify

```bash
cd ~/ecg-service/functions_python
ls -la
```

You should see: `main.py`, `Dockerfile`, `requirements.txt`, `transformers/`, etc.
