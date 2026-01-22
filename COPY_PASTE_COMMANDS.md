# Copy-Paste Commands for Deployment

Copy and paste these commands **one at a time** into your PowerShell terminal.

## Step 1: Authenticate with Google Cloud
```powershell
gcloud auth login
```
*(This will open a browser - complete the login)*

## Step 2: Set the Project
```powershell
gcloud config set project hv-ecg
```

## Step 3: Enable Required APIs
```powershell
gcloud services enable cloudbuild.googleapis.com
```
```powershell
gcloud services enable run.googleapis.com
```

## Step 4: Navigate to Python Service Directory
```powershell
cd functions_python
```

## Step 5: Build Docker Image
```powershell
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
```
*(This takes 5-10 minutes - wait for it to complete)*

## Step 6: Deploy to Cloud Run
```powershell
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi --timeout 300 --max-instances 10
```
*(After this completes, you'll see a "Service URL" - COPY IT!)*

## Step 7: Go Back to Project Root
```powershell
cd ..
```

## Step 8: Set Firebase Config with Your Service URL
*(Replace YOUR_SERVICE_URL_HERE with the URL from Step 6)*
```powershell
firebase functions:config:set python.multi_method_url="YOUR_SERVICE_URL_HERE"
```

## Step 9: Deploy Cloud Function
```powershell
firebase deploy --only functions:processMultiMethodTransform
```

## Done! 

Now try "Process All Methods" in the gallery - it should work!
