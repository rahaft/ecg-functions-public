# Get Firebase Admin Credentials

## Quick Option: Use Firebase CLI

The easiest way is to use Firebase CLI which handles authentication automatically:

```powershell
# Install Firebase CLI if needed
npm install -g firebase-tools

# Login to Firebase
firebase login

# This will authenticate and allow Firebase Admin SDK to work
```

Then run the import with:
```powershell
python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
```

## Alternative: Download Service Account Key

1. **Go to:** https://console.firebase.google.com/project/hv-ecg/settings/serviceaccounts/adminsdk

2. **Click:** "Generate new private key"

3. **Click:** "Generate key" (file downloads as JSON)

4. **Save the file as:** `serviceAccountKey.json` in your project root

5. **Run import:**
   ```powershell
   python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json
   ```

## After Getting Credentials

Once you have `serviceAccountKey.json`:
- ✅ Place it in project root: `C:\Users\Rosi\Documents\Maxone Backup\Rosi\Gauntlet2\hat_ecg\serviceAccountKey.json`
- ✅ Run: `python scripts/import_gcs_manifest_to_firestore.py image_manifest_gcs.json`
- ✅ This will import all 8,795 images to Firestore `kaggle_images` collection

## Then Build Backend

After import, we can:
1. Add Firebase functions to access images
2. Update training viewer to display them
3. Add digitization testing interface
