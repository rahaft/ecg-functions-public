# ECG Image Digitization - Firebase Web Application

A Firebase-based web application for uploading and digitizing ECG images. Supports multiple image uploads per ECG record and provides a foundation for the digitization pipeline.

## Features

- 🔐 **Anonymous Authentication** - Quick sign-in without registration
- 📤 **Multi-file Upload** - Upload multiple images for a single ECG record
- 📊 **Record Management** - View and manage all your ECG records
- 🔄 **Real-time Updates** - See record status updates in real-time
- 📱 **Responsive Design** - Works on desktop and mobile devices

## Setup Instructions

### 1. Firebase Project Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Enable the following services:
   - **Authentication**: Enable Anonymous authentication
   - **Firestore Database**: Create database in test mode (rules will be updated)
   - **Storage**: Create storage bucket

### 2. Get Firebase Configuration

1. In Firebase Console, go to Project Settings
2. Scroll down to "Your apps" section
3. Click the web icon (`</>`) to add a web app
4. Copy the Firebase configuration object

### 3. Configure the Application

1. Open `public/index.html`
2. Replace the Firebase configuration in the `<script type="module">` section:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};
```

### 4. Update Firebase Project ID

1. Open `.firebaserc`
2. Replace `"your-project-id"` with your actual Firebase project ID

### 5. Deploy Firebase Rules

```bash
firebase deploy --only firestore:rules,storage:rules
```

### 6. Install Firebase CLI (if not already installed)

```bash
npm install -g firebase-tools
```

### 7. Login to Firebase

```bash
firebase login
```

### 8. Initialize Firebase (if needed)

```bash
firebase init
```

Select:
- Firestore
- Storage
- Hosting

### 9. Deploy the Application

```bash
firebase deploy
```

Or deploy only hosting:

```bash
firebase deploy --only hosting
```

## Local Development

### Option 1: Firebase Hosting Emulator

```bash
firebase emulators:start --only hosting
```

Then visit `http://localhost:5000`

### Option 2: Simple HTTP Server

```bash
cd public
python -m http.server 8000
# or
npx serve public
```

Then visit `http://localhost:8000`

**Note**: For local development without emulators, you'll need to configure CORS in Firebase Storage and Firestore rules to allow localhost access, or use the Firebase emulators.

## Project Structure

```
.
├── public/                 # Web application files
│   ├── index.html         # Main HTML file
│   ├── styles.css         # Styling
│   └── app.js             # Application logic
├── functions/             # Cloud Functions (future)
├── firebase.json          # Firebase configuration
├── .firebaserc            # Firebase project settings
├── firestore.rules        # Firestore security rules
├── storage.rules          # Storage security rules
└── README.md             # This file
```

## Data Model

### Firestore Collections

#### `ecg_records`
- `userId` (string): User ID
- `recordId` (string): User-provided record identifier
- `status` (string): `uploading`, `uploaded`, `processing`, `completed`, `error`
- `imageCount` (number): Number of images
- `imageUrls` (array): Download URLs for images
- `createdAt` (timestamp): Creation time
- `updatedAt` (timestamp): Last update time

#### `ecg_records/{recordId}/images`
- `fileName` (string): Original filename
- `fileSize` (number): File size in bytes
- `fileType` (string): MIME type
- `storagePath` (string): Storage path
- `downloadUrl` (string): Download URL
- `uploadedAt` (timestamp): Upload time

#### `ecg_records/{recordId}/results` (future)
- Processing results and digitized signals

### Storage Structure

```
ecg_images/
  └── {userId}/
      └── {recordId}/
          ├── image1.png
          ├── image2.jpg
          └── ...
```

## Next Steps

### Phase 1: Complete Upload System ✅
- [x] Firebase setup
- [x] Authentication
- [x] File upload
- [x] Record management

### Phase 2: Digitization Pipeline ✅
- [x] Image preprocessing module
- [x] Signal extraction
- [x] Calibration and scaling
- [x] Post-processing
- [x] Cloud Functions for processing
- [x] Python digitization pipeline

### Phase 3: Visualization ✅
- [x] Display uploaded images
- [x] Show extracted signals
- [x] Interactive charts
- [x] Download results
- [x] Export formats (JSON, CSV, Kaggle submission)

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Node.js Cloud Functions
- Python digitization pipeline (Cloud Run or Cloud Functions)
- Environment configuration

## Security Notes

- The current setup uses anonymous authentication for quick setup
- For production, consider implementing proper user authentication
- Review and adjust Firestore and Storage rules based on your security requirements
- The rules currently allow users to only access their own data

## Troubleshooting

### Upload fails
- Check Firebase Storage rules
- Verify authentication is working
- Check browser console for errors

### Records not showing
- Verify Firestore rules are deployed
- Check that queries are using correct user ID
- Check browser console for errors

### CORS errors in local development
- Use Firebase emulators for local development
- Or configure CORS in Firebase Storage settings

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here]
