# Find the Uploaded Zip File

The file is in Cloud Shell but not in the expected location. Let's find it.

## Method 1: Comprehensive Search

In Cloud Shell terminal, run:

```bash
find ~ -name "*functions_python*.zip" -type f 2>/dev/null
```

This searches for any zip file with "functions_python" in the name.

## Method 2: Check Editor Workspace

Files uploaded via File menu often go to a workspace directory. Try:

```bash
ls -la ~/.codeoss/workspace/
ls -la ~/.codeoss/
```

Or check for any workspace folders:

```bash
find ~ -type d -name "*workspace*" 2>/dev/null
```

## Method 3: Use File Explorer Path

In Cloud Shell Editor:
1. Look at the left sidebar (File Explorer)
2. Find `functions_python.zip` (or `functions_functions_python.zip`) in the file tree
3. Click on the folder icon above it to see the full path
4. The path will be shown in the explorer

## Method 4: Check All Zip Files

```bash
find ~ -name "*.zip" -type f 2>/dev/null
```

This will show ALL zip files, which might help identify where uploads go.

## Once Found

Once you have the path (e.g., `/home/yourname/.codeoss/workspace/functions_python.zip`):

```bash
# Move it to ecg-service
mkdir -p ~/ecg-service
mv /full/path/to/functions_python.zip ~/ecg-service/
cd ~/ecg-service
unzip functions_python.zip
cd functions_python
ls -la
```
