# Storage Trigger Deployment Fix

## Current Issue
The `processECGImage` Storage trigger is failing to deploy with error:
"Failed to configure trigger providers/cloud.storage/eventTypes/object.change"

## Why This Happens
1. Storage triggers require specific IAM permissions (usually auto-granted)
2. The Cloud Functions service account needs Storage Object Admin role
3. Sometimes the trigger needs to be deployed after Storage API is fully enabled

## Solutions

### Option 1: Wait and Retry (Recommended First)
After enabling Cloud Functions API, wait 2-3 minutes, then:
```powershell
firebase deploy --only "functions:processECGImage"
```

### Option 2: Use Manual Processing (Workaround)
Since `processRecord` and `generateSubmission` deployed successfully, you can:
- Upload images normally
- Manually trigger processing via the "Process" button in the UI
- The `processRecord` function will handle all images for a record

### Option 3: Check Storage Bucket Configuration
1. Go to [Firebase Console](https://console.firebase.google.com/) → Storage
2. Ensure the default bucket exists
3. Check that Storage rules are deployed

### Option 4: Alternative Trigger Method
If Storage trigger continues to fail, we can modify the function to:
- Use HTTP trigger instead
- Call it manually from the frontend after upload
- Or use Firestore triggers as an alternative

## Current Status
✅ `processRecord` - Deployed successfully  
✅ `generateSubmission` - Deployed successfully  
❌ `processECGImage` - Storage trigger configuration issue

## Recommendation
For now, use the manual `processRecord` function. The Storage trigger is a convenience feature but not essential for the app to work.
