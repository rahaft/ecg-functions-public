# ECG Image Gallery - Overview

## Purpose
The ECG Image Gallery is a web-based application for viewing, organizing, and testing ECG (electrocardiogram) image digitization algorithms. It provides tools to compare ground truth images with transformed images and analyze the accuracy of digitization methods.

## URL
**Live Site:** https://hv-ecg.web.app/gallery.html

## Key Features

### 1. **Authentication**
- **Anonymous Sign-In**: Quick access without registration
- **Google Sign-In**: Optional authenticated access
- **Auto-login**: Automatically signs in when page loads
- **User Display**: Shows current user (email or anonymous ID)

### 2. **Image Loading & Filtering**
- **Subset Filter**: Filter by:
  - All Images
  - Training Set (train)
  - Test Set (test)
- **Grouping Options**:
  - **Filename Prefix** (default): Groups images by prefix before the "-" (e.g., `1006427285-0001.png`, `1006427285-0002.png` → Group "1006427285")
  - **Folder**: Groups by folder structure
  - **No Grouping**: Shows all images in a flat list
- **Lazy Loading**: 
  - Initial load: 20 images
  - "Load More" button to load additional batches
  - Max limit: 10,000 images (configurable)
- **Image Source**: Loads from Google Cloud Storage (GCS) buckets:
  - `ecg-competition-data-1` through `ecg-competition-data-5`
  - Images stored in Firestore `kaggle_images` collection

### 3. **Image Display**
- **Grouped View**: Images organized by groups with:
  - Group header showing prefix/folder name
  - Preview image (first image in group)
  - Image count per group
  - "Select All" button for group
- **Image Cards**: Each image shows:
  - Thumbnail preview
  - Filename
  - File size
  - Train/Test indicator
  - Action buttons: **Test**, **Select**, **Compare**
- **Image Loading**:
  - Queue system limits concurrent requests (max 5)
  - Tries public GCS URLs first
  - Falls back to signed URLs if needed
  - Error placeholders for failed loads

### 4. **Image Comparison Modal**
Opens when clicking an image or "Compare" button (for images in groups with ground truth).

#### View Options
- **Dropdown Selector**: [ Both | Sample | To Transform ]
  - **Both**: Side-by-side comparison
  - **Sample**: Ground truth only (full width)
  - **To Transform**: Transform image only (full width)

#### Grid Settings (Collapsible)
- **Standard ECG Grid Measurements**:
  - Small Square: 1mm × 1mm = 0.04 seconds / 0.1 mV
  - Large Square: 5mm × 5mm = 0.20 seconds / 0.5 mV
- **Scale Controls**:
  - Image Length (mm): Enter physical length
  - Image Width (mm): Enter physical width
  - Auto-calculates grid pixel sizes from mm dimensions
- **Grid Adjustments**:
  - Small Square Width (pixels): Default 20px
  - Large Square Width (pixels): Default 100px (5× small)
  - Show/Hide Grid Overlay checkbox
- **Grid Overlay**: 
  - Visual grid overlay on images
  - Small grid lines (light gray) every 1mm
  - Large grid lines (darker gray) every 5mm
  - Scales with image size

#### Algorithm Visualization
- **4th Degree Polynomial Mapping**:
  - Interactive canvas showing mapping curve
  - Grid background for reference
  - Control points (clickable) every 5%
  - Line position slider for navigation
- **Polynomial Coefficients**:
  - A (t⁴): 4th degree coefficient
  - B (t³): 3rd degree coefficient
  - C (t²): 2nd degree coefficient
  - D (t): Linear coefficient
  - E: Constant term
- **Legend**:
  - Light Gray: Small grid lines (1mm)
  - Dark Gray: Large grid lines (5mm)
  - Blue: Polynomial mapping curve
  - Green: Control points
  - Red: Line position indicator
- **Point Inspection**:
  - Click any point to see:
    - Grid position (large & small squares)
    - Time in seconds/milliseconds
    - Voltage in mV
    - Polynomial parameter and value

### 5. **Digitization Testing**
- **Individual Test**: "Test" button on each image
  - Processes image through digitization algorithm
  - Returns mock results (algorithm integration pending)
- **Group Testing**: "Test All in Group" button
  - Compares all images in group against ground truth (-0001)
  - Uses `compareWithGroundTruth` Cloud Function
  - Shows accuracy scores:
    - Overall accuracy percentage
    - Per-lead scores
    - Correlation, MSE, SSIM metrics
  - Color-coded results:
    - Green: ≥90% accuracy
    - Orange: ≥70% accuracy
    - Red: <70% accuracy

### 6. **Image Selection**
- **Toggle Selection**: Click image card or "Select" button
- **Group Selection**: "Select All" button selects entire group
- **Selection Stats**: Shows count of selected images
- **Visual Feedback**: Selected images highlighted in green

### 7. **Statistics Dashboard**
- **Total Images**: Count of all loaded images
- **Groups**: Number of image groups
- **Selected**: Count of currently selected images

### 8. **Version Control**
- **Version Display**: Shows app version, build timestamp, deployment date
- **Console Logging**: Version info logged to console
- **Footer**: Version info displayed in page footer

## Technical Architecture

### Frontend
- **Framework**: Vanilla JavaScript (ES6 modules)
- **UI**: HTML5 + CSS3 with responsive design
- **Firebase SDK**: v10.7.1
  - Authentication
  - Firestore (database)
  - Cloud Functions (backend API)
  - Storage (image URLs)

### Backend (Cloud Functions)
- **`listGCSImages`**: Lists images from Firestore with filtering
- **`getGCSImageUrl`**: Generates signed URLs for GCS images
- **`processGCSImage`**: Processes image through digitization
- **`compareWithGroundTruth`**: Compares digitized results with ground truth

### Data Flow
1. User signs in (anonymous or Google)
2. Frontend calls `listGCSImages` with filters
3. Images loaded from Firestore `kaggle_images` collection
4. Images grouped by prefix/folder
5. Public GCS URLs used for display (with signed URL fallback)
6. Comparison modal loads both images
7. Grid overlay drawn based on settings
8. Algorithm visualization shows polynomial mapping
9. Testing calls Cloud Functions for processing

### Image Storage
- **GCS Buckets**: 5 buckets (`ecg-competition-data-1` through `-5`)
- **Firestore Collection**: `kaggle_images`
  - Fields: `filename`, `gcs_bucket`, `gcs_path`, `gcs_url`, `is_train`, `is_test`, `folder`
- **Public Access**: Buckets configured for public read access
- **CORS**: Configured to allow web app access

## User Workflow

### Basic Viewing
1. Sign in (automatic or manual)
2. Select subset (All/Train/Test)
3. Choose grouping method
4. Click "Load Images"
5. Browse grouped images
6. Click "Load More" for additional images

### Image Comparison
1. Click an image or "Compare" button
2. Modal opens with ground truth and transform images
3. Use dropdown to switch views (Both/Sample/Transform)
4. Adjust grid settings (expand/collapse section)
5. Enter image dimensions in mm for auto-scaling
6. Toggle grid overlay on/off
7. View algorithm visualization
8. Adjust polynomial coefficients
9. Click points to inspect details
10. Use line position slider to navigate

### Testing Digitization
1. Click "Test" on individual image
2. Or click "Test All in Group" for batch testing
3. View accuracy results in test panel
4. See per-lead breakdowns
5. Review correlation, MSE, SSIM metrics

## Key Files
- **`public/gallery.html`**: Main gallery page (single-file application)
- **`functions/index.js`**: Cloud Functions for backend operations
- **`functions/compareAccuracy.js`**: Accuracy calculation module

## Future Enhancements
- [ ] Real digitization algorithm integration (currently mocked)
- [ ] Box skewing detection UI
- [ ] Enhanced point intersection navigation
- [ ] Visual overlay comparison
- [ ] Export results functionality
- [ ] Batch processing capabilities

## Version
**Current Version**: 1.7.0
**Last Updated**: 2026-01-20
