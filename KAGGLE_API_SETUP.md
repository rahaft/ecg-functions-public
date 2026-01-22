# Kaggle API Setup for Firebase Functions

## Your Kaggle API Token

- **Username**: `raconcilio`
- **API Token**: `KGAT_63eff21566308d9247d9247d9336796c43581`
- **Credentials saved to**: `~/.kaggle/kaggle.json`

## Set Token in Firebase Functions

To use Kaggle API in Firebase Functions, set the environment variable:

```bash
# Set in Firebase Functions config
firebase functions:config:set kaggle.api_token="KGAT_63eff21566308d9247d9336796c43581"
firebase functions:config:set kaggle.username="raconcilio"

# Then deploy functions
firebase deploy --only functions
```

## Alternative: Environment Variable

For Cloud Functions, you can also set environment variables in Firebase Console:
1. Go to Firebase Console → Functions → Environment Variables
2. Add `KAGGLE_API_TOKEN` = `KGAT_63eff21566308d9247d9336796c43581`
3. Add `KAGGLE_USERNAME` = `raconcilio`

## Testing Locally

The credentials are already saved locally at `~/.kaggle/kaggle.json`.

To test:
```bash
python scripts/kaggle_setup.py test
python scripts/kaggle_setup.py list physionet-ecg-image-digitization
```

## Current Status

✅ Kaggle credentials saved locally
✅ Firebase Functions code updated to use Kaggle API
✅ Frontend ready to call the API
⚠️  Firebase Functions need to be deployed with the token

## Next Steps

1. **Set Firebase Functions config** (see command above)
2. **Deploy Functions**: `firebase deploy --only functions`
3. **Test on live site**: Visit `https://hv-ecg.web.app/training_viewer.html`
4. **Click "Import Images from Kaggle"**

The interface will automatically fetch images from the competition and display them for comparison!
