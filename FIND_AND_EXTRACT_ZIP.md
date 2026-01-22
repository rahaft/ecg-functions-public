# Find and Extract the Zip File

## Step 1: Find Where the Zip File Was Uploaded

In Cloud Shell terminal, run:

```bash
find ~ -name "functions_python.zip" 2>/dev/null
```

This will show you where the zip file is located.

## Step 2: Navigate to That Location

Once you find it, navigate there. It's likely in:
- `~/` (home directory)
- `~/ecg-service/` (if it was uploaded there)
- Or wherever the File menu uploaded it

## Step 3: Move to Correct Directory

If the zip is in your home directory (`~`), move it to `ecg-service`:

```bash
cd ~
ls -la functions_python.zip
# If it's here, move it:
mkdir -p ~/ecg-service
mv functions_python.zip ~/ecg-service/
```

## Step 4: Extract

```bash
cd ~/ecg-service
unzip functions_python.zip
```

## Step 5: Verify

```bash
cd functions_python
ls -la
```

You should see: `main.py`, `Dockerfile`, `requirements.txt`, `transformers/`, etc.
