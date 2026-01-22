# Locate and Extract the Zip File

The zip file is uploaded but in a different location. Let's find it.

## Step 1: Find the Zip File

In Cloud Shell terminal, run:

```bash
find ~ -name "functions_python.zip" -type f 2>/dev/null
```

This will show the full path where the file is located.

## Step 2: Check Editor Workspace

Files uploaded via File menu often go to the editor's workspace. Try:

```bash
ls -la ~/.codeoss/
ls -la ~/.codeoss/workspace/
```

Or check if there's a workspace folder:

```bash
ls -la ~/ | grep -i workspace
```

## Step 3: Once Found, Move and Extract

Once you find the file path (let's say it's at `/path/to/functions_python.zip`):

```bash
# Move it to ecg-service
mkdir -p ~/ecg-service
mv /path/to/functions_python.zip ~/ecg-service/
cd ~/ecg-service
unzip functions_python.zip
```

## Step 4: Alternative - Use File Explorer

In Cloud Shell Editor:
1. Look at the left sidebar (File Explorer)
2. Find `functions_python.zip` in the file tree
3. Note the folder path shown above it
4. In terminal, navigate to that path:
   ```bash
   cd /path/from/explorer
   ls -la functions_python.zip
   ```

## Step 5: Verify After Extraction

```bash
cd ~/ecg-service/functions_python
ls -la
```

You should see: `main.py`, `Dockerfile`, `requirements.txt`, `transformers/`, etc.
