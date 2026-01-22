# Deploy Pipeline Test to Firebase

## Quick Deploy

To add the pipeline test page to your Firebase website (`https://hv-ecg.web.app/`):

### 1. Deploy the New Page

```bash
firebase deploy --only hosting
```

This will deploy `public/pipeline_test.html` to your Firebase hosting.

### 2. Access the Page

After deployment, visit:
```
https://hv-ecg.web.app/pipeline_test.html
```

## Current Status

The page is created but needs backend integration. To fully enable it:

### Option 1: Connect to Local Test Server (Development)

For local testing, run the Python live test server:
```bash
cd functions_python
python live_test_server.py
```

Then you can modify `pipeline_test.html` to point to `http://localhost:5000/process` for testing.

### Option 2: Deploy Python Pipeline to Cloud Run (Production)

1. Deploy the Python pipeline as a Cloud Run service
2. Update `functions/index.js` to call the Cloud Run service
3. Update `pipeline_test.html` to use Firebase Functions

### Option 3: Integrate into Existing Firebase Functions

Update your existing Firebase Functions (`functions/index.js`) to use the enhanced pipeline by:
1. Installing Python dependencies in Cloud Functions
2. Calling the digitization pipeline from Node.js functions
3. Processing images when uploaded to Firebase Storage

## Testing on Your Firebase Site

Once deployed, you can test at:
- **Main App**: https://hv-ecg.web.app/
- **Pipeline Test**: https://hv-ecg.web.app/pipeline_test.html

## Next Steps

1. **Deploy the page**: `firebase deploy --only hosting`
2. **Test the page**: Visit `https://hv-ecg.web.app/pipeline_test.html`
3. **Connect backend**: Integrate with Cloud Functions or Cloud Run
