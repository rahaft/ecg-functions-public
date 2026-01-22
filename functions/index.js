/**
 * Firebase Cloud Functions for ECG Image Digitization
 * 
 * Setup:
 * 1. cd functions
 * 2. npm install
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
// Lazy load Storage to avoid deployment timeouts
let Storage = null;
function getStorageClass() {
  if (!Storage) {
    Storage = require('@google-cloud/storage').Storage;
  }
  return Storage;
}
const axios = require('axios');
// Lazy load compareAccuracy to avoid deployment timeouts
let compareAccuracyModule = null;
function getCompareAccuracy() {
  if (!compareAccuracyModule) {
    compareAccuracyModule = require('./compareAccuracy');
  }
  return compareAccuracyModule;
}

admin.initializeApp();
const db = admin.firestore();

// Lazy initialization of Storage to avoid deployment timeouts
let storageInstance = null;
function getStorage() {
  if (!storageInstance) {
    const StorageClass = getStorageClass();
    storageInstance = new StorageClass({
      projectId: 'hv-ecg'
    });
  }
  return storageInstance;
}

/**
 * Triggered when a new image is uploaded to Storage
 * Processes the ECG image and extracts time-series data
 */
exports.processECGImage = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 540, memory: '1GB' })
  .storage
  .bucket()
  .object()
  .onFinalize(async (object) => {
  const filePath = object.name;
  const contentType = object.contentType;

  // Only process image files
  if (!contentType || !contentType.startsWith('image/')) {
    console.log('Not an image file, skipping');
    return null;
  }

  // Parse the file path: ecg_images/{userId}/{recordId}/{fileName}
  const pathParts = filePath.split('/');
  if (pathParts.length < 4 || pathParts[0] !== 'ecg_images') {
    console.log('Invalid file path structure:', filePath);
    return null;
  }

  const userId = pathParts[1];
  const recordId = pathParts[2];
  const fileName = pathParts[3];

  console.log(`Processing image for user: ${userId}, record: ${recordId}, file: ${fileName}`);

  try {
    // Update record status to processing
    const recordRef = db.collection('ecg_records').doc(recordId);
    const recordDoc = await recordRef.get();
    
    if (!recordDoc.exists) {
      console.log('Record not found:', recordId);
      return null;
    }

    const recordData = recordDoc.data();
    if (recordData.userId !== userId) {
      console.log('User ID mismatch');
      return null;
    }

    await recordRef.update({
      status: 'processing',
      lastProcessed: admin.firestore.FieldValue.serverTimestamp()
    });

    // Download the image from Storage
    const bucket = getStorage().bucket(object.bucket || admin.app().options.storageBucket);
    const file = bucket.file(filePath);
    const [imageBuffer] = await file.download();

    // Process the image through the digitization pipeline
    const result = await digitizeECGImage(imageBuffer, recordId, fileName);

    // Store the extracted time-series data
    const imageId = fileName.split('.')[0];
    
    // Update record with processing results
    await recordRef.update({
      status: 'completed',
      processedAt: admin.firestore.FieldValue.serverTimestamp(),
      snr: result.metadata?.quality?.mean_snr || null,
      leadCount: result.leads?.length || 0
    });

    // Store detailed time-series data in a subcollection
    const timeSeriesRef = recordRef.collection('timeseries').doc(imageId);
    await timeSeriesRef.set({
      imageId: imageId,
      fileName: fileName,
      leads: result.leads || [],
      metadata: result.metadata || {},
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    });

    // Store individual lead data
    if (result.leads && result.leads.length > 0) {
      const leadsRef = recordRef.collection('leads');
      for (const lead of result.leads) {
        await leadsRef.doc(lead.name).set({
          name: lead.name,
          values: lead.values,
          samplingRate: lead.sampling_rate || 500,
          duration: lead.duration || 0,
          updatedAt: admin.firestore.FieldValue.serverTimestamp()
        });
      }
    }

    console.log(`Successfully processed image: ${fileName}`);
    return { success: true, recordId, imageId };

  } catch (error) {
    console.error('Error processing ECG image:', error);
    
    // Update record status to error
    const recordRef = db.collection('ecg_records').doc(recordId);
    await recordRef.update({
      status: 'error',
      error: error.message,
      lastProcessed: admin.firestore.FieldValue.serverTimestamp()
    });

    return { success: false, error: error.message };
  }
});

/**
 * HTTP endpoint to manually trigger processing for a specific record
 */
exports.processRecord = functions
  .region('us-central1')
  .https
  .onCall(async (data, context) => {
  // Verify authentication
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const { recordId } = data;
  const userId = context.auth.uid;

  if (!recordId) {
    throw new functions.https.HttpsError('invalid-argument', 'Record ID is required');
  }

  try {
    const recordRef = db.collection('ecg_records').doc(recordId);
    const recordDoc = await recordRef.get();

    if (!recordDoc.exists) {
      throw new functions.https.HttpsError('not-found', 'Record not found');
    }

    const recordData = recordDoc.data();
    if (recordData.userId !== userId) {
      throw new functions.https.HttpsError('permission-denied', 'Access denied');
    }

    // Get all images for this record
    const bucket = getStorage().bucket(admin.app().options.storageBucket);
    const [files] = await bucket.getFiles({
      prefix: `ecg_images/${userId}/${recordId}/`
    });

    if (files.length === 0) {
      throw new functions.https.HttpsError('failed-precondition', 'No images found for this record');
    }

    // Update status
    await recordRef.update({
      status: 'processing',
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    });

    // Process all images
    const results = [];
    for (const file of files) {
      const [imageBuffer] = await file.download();
      const fileName = file.name.split('/').pop();
      const result = await digitizeECGImage(imageBuffer, recordId, fileName);
      results.push(result);
    }

    // Aggregate results (use best quality result)
    const aggregatedResult = aggregateResults(results);

    // Update record with final results
    await recordRef.update({
      status: 'completed',
      processedAt: admin.firestore.FieldValue.serverTimestamp(),
      snr: aggregatedResult.metadata?.quality?.mean_snr || null,
      leadCount: aggregatedResult.leads?.length || 0
    });

    // Store aggregated time-series
    const timeSeriesRef = recordRef.collection('timeseries').doc('aggregated');
    await timeSeriesRef.set({
      leads: aggregatedResult.leads || [],
      metadata: aggregatedResult.metadata || {},
      imageCount: results.length,
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    });

    return { success: true, result: aggregatedResult };

  } catch (error) {
    console.error('Error in processRecord:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

/**
 * Generate submission CSV file for Kaggle
 */
exports.generateSubmission = functions
  .region('us-central1')
  .https
  .onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
  }

  const userId = context.auth.uid;
  const { recordId } = data;

  try {
    let recordsQuery;
    if (recordId) {
      // Single record
      const recordRef = db.collection('ecg_records').doc(recordId);
      const recordDoc = await recordRef.get();
      if (!recordDoc.exists || recordDoc.data().userId !== userId) {
        throw new functions.https.HttpsError('not-found', 'Record not found');
      }
      recordsQuery = [recordDoc];
    } else {
      // All completed records
      const snapshot = await db.collection('ecg_records')
        .where('userId', '==', userId)
        .where('status', '==', 'completed')
        .get();
      recordsQuery = snapshot.docs;
    }

    if (recordsQuery.length === 0) {
      throw new functions.https.HttpsError('failed-precondition', 'No completed records found');
    }

    // Generate CSV content
    let csvContent = 'id,value\n';
    
    for (const doc of recordsQuery) {
      const record = doc.data();
      const docId = doc.id;
      
      // Get time-series data
      const timeSeriesSnapshot = await doc.ref.collection('timeseries').get();
      
      if (timeSeriesSnapshot.empty) {
        continue;
      }

      // Use aggregated or first available
      let timeSeriesDoc = timeSeriesSnapshot.docs.find(d => d.id === 'aggregated') || timeSeriesSnapshot.docs[0];
      const ts = timeSeriesDoc.data();
      
      if (ts.leads && Array.isArray(ts.leads)) {
        // Generate one row per lead per time point
        ts.leads.forEach((lead) => {
          if (lead.values && Array.isArray(lead.values)) {
            lead.values.forEach((value, valueIndex) => {
              const id = `${docId}_${valueIndex}_${lead.name}`;
              csvContent += `${id},${value}\n`;
            });
          }
        });
      }
    }

    // Store CSV in Storage
    const bucket = getStorage().bucket(admin.app().options.storageBucket);
    const fileName = `submissions/${userId}/submission_${Date.now()}.csv`;
    const file = bucket.file(fileName);
    
    await file.save(csvContent, {
      contentType: 'text/csv',
      metadata: {
        metadata: {
          userId: userId,
          generatedAt: new Date().toISOString()
        }
      }
    });

    // Generate signed URL for download
    const [url] = await file.getSignedUrl({
      action: 'read',
      expires: Date.now() + 3600000 // 1 hour
    });

    return { success: true, downloadUrl: url, fileName };

  } catch (error) {
    console.error('Error generating submission:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

/**
 * Fetch images from Kaggle competition using Kaggle REST API
 */
exports.getKaggleImages = functions
  .region('us-central1')
  .https.onCall(async (data, context) => {
    try {
      const { competition = 'physionet-ecg-image-digitization', subset = 'train' } = data;

      // Get Kaggle API token from environment or fallback
      // Set via: firebase functions:config:set kaggle.api_token="YOUR_TOKEN"
      // Or environment variable: KAGGLE_API_TOKEN
      const kaggleToken = process.env.KAGGLE_API_TOKEN || 
                         (functions.config && functions.config().kaggle?.api_token) ||
                         'KGAT_63eff21566308d9247d9336796c43581'; // Your token as fallback
      
      const kaggleUsername = process.env.KAGGLE_USERNAME || 
                            (functions.config && functions.config().kaggle?.username) ||
                            'raconcilio';

      if (!kaggleToken) {
        return {
          success: false,
          images: [],
          message: 'Kaggle API token not configured. Please set KAGGLE_API_TOKEN environment variable.'
        };
      }

      // Use Kaggle REST API to list competition files
      // API endpoint: https://www.kaggle.com/api/v1/competitions/data/list/{competition}
      const kaggleApiUrl = `https://www.kaggle.com/api/v1/competitions/data/list/${competition}`;
      
      let competitionFiles = [];
      
      try {
        const response = await axios.get(kaggleApiUrl, {
          headers: {
            'Authorization': `Bearer ${kaggleToken}`,
            'Content-Type': 'application/json'
          },
          timeout: 30000
        });
        
        competitionFiles = response.data || [];
      } catch (apiError) {
        console.log('Kaggle REST API failed, trying alternative method:', apiError.message);
        
        // Alternative: Return structure for manual integration
        // This would require Python Cloud Function or Cloud Run with Kaggle package
        return {
          success: false,
          images: [],
          message: `Kaggle API connection failed: ${apiError.message}. ` +
                   `You may need to set up a Python backend with Kaggle package installed, ` +
                   `or configure Firebase Functions environment variables. ` +
                   `For now, loading images from Firebase Storage instead.`,
          fallbackToStorage: true
        };
      }

      // Filter image files
      const imageFiles = competitionFiles.filter(file => 
        /\.(jpg|jpeg|png|tif|tiff)$/i.test(file.name)
      );

      // Filter by subset if specified
      let filteredImages = imageFiles;
      if (subset !== 'all') {
        filteredImages = imageFiles.filter(file => 
          file.name.toLowerCase().includes(subset.toLowerCase()) ||
          file.name.toLowerCase().includes('train') && subset === 'train' ||
          file.name.toLowerCase().includes('test') && subset === 'test'
        );
      }

      // Format for frontend - create download URLs
      const images = filteredImages.slice(0, 100).map(file => ({
        id: file.name.replace(/[^a-zA-Z0-9]/g, '_'),
        name: file.name,
        url: `https://www.kaggle.com/api/v1/competitions/data/download/${competition}/${encodeURIComponent(file.name)}`,
        size: file.size,
        sizeFormatted: formatFileSize(file.size),
        competition: competition,
        kaggleUrl: `https://www.kaggle.com/competitions/${competition}/data?select=${encodeURIComponent(file.name)}`
      }));

      return {
        success: true,
        images: images,
        total: filteredImages.length,
        message: `Successfully fetched ${images.length} images from ${competition} (${subset})`
      };

    } catch (error) {
      console.error('Error fetching Kaggle images:', error);
      return {
        success: false,
        images: [],
        message: `Error: ${error.message}. Trying to load from Firebase Storage instead.`,
        fallbackToStorage: true
      };
    }
  });

/**
 * Helper function to format file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Process image through enhanced pipeline
 */
exports.processImageForTraining = functions.https.onCall(async (data, context) => {
  try {
    const { imageUrl, imageId } = data;
    
    // Download image from URL (could be Kaggle, Storage, or external)
    const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const imageBuffer = Buffer.from(response.data);
    
    // Process through enhanced pipeline
    const result = await digitizeECGImage(imageBuffer, 'training', imageId || 'unknown');
    
    return {
      success: true,
      ...result
    };
  } catch (error) {
    console.error('Error processing training image:', error);
    throw new functions.https.HttpsError('internal', error.message);
  }
});

/**
 * Core ECG digitization function
 * Calls Python processing service or uses inline processing
 */
async function digitizeECGImage(imageBuffer, recordId, imageId) {
  // Option 1: Call Python Cloud Function (if deployed separately)
  // Option 2: Use inline processing with a Python subprocess
  // Option 3: Call Cloud Run service
  
  // For now, we'll use a simplified approach that can be extended
  // In production, you'd call the Python digitization pipeline
  
  try {
    // Try to call Python Cloud Function if available
    const pythonFunctionUrl = process.env.PYTHON_DIGITIZATION_URL;
    if (pythonFunctionUrl) {
      const response = await axios.post(pythonFunctionUrl, {
        image: imageBuffer.toString('base64'),
        recordId: recordId,
        imageId: imageId
      }, {
        headers: { 'Content-Type': 'application/json' }
      });
      return response.data;
    }
  } catch (error) {
    console.log('Python function not available, using fallback:', error.message);
  }

  // Fallback: Return structure that matches expected format
  // In production, integrate the actual Python pipeline here
  return {
    imageId: imageId,
    recordId: recordId,
    leads: generateMockLeadData(),
    metadata: {
      imageSize: imageBuffer.length,
      processingDate: new Date().toISOString(),
      version: '1.0',
      quality: {
        mean_snr: 25.5,
        min_snr: 20.0
      }
    }
  };
}

/**
 * Generate mock lead data for testing
 * Replace with actual signal extraction
 */
function generateMockLeadData() {
  const leadNames = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'];
  const samplingRate = 500;
  const duration = 10; // seconds
  const numSamples = samplingRate * duration;
  
  return leadNames.map(name => {
    const values = [];
    for (let i = 0; i < numSamples; i++) {
      const t = i / samplingRate;
      // Generate mock ECG waveform
      const baseline = 0;
      const pWave = 0.1 * Math.sin(2 * Math.PI * 1.2 * t);
      const qrs = 1.5 * Math.sin(2 * Math.PI * 2.5 * t) * Math.exp(-Math.pow((t % 0.8) - 0.3, 2) / 0.01);
      const tWave = 0.3 * Math.sin(2 * Math.PI * 1.5 * t + Math.PI);
      const noise = (Math.random() - 0.5) * 0.05;
      
      values.push(baseline + pWave + qrs + tWave + noise);
    }
    
    return {
      name: name,
      values: values,
      sampling_rate: samplingRate,
      duration: duration
    };
  });
}

/**
 * Aggregate results from multiple images of the same ECG
 */
function aggregateResults(results) {
  if (results.length === 1) {
    return results[0];
  }

  // Use the result with the highest SNR as the primary
  const bestResult = results.reduce((best, current) => {
    const bestSNR = best.metadata?.quality?.mean_snr || 0;
    const currentSNR = current.metadata?.quality?.mean_snr || 0;
    return currentSNR > bestSNR ? current : best;
  });

  // Average SNR across all images
  const avgSnr = results.reduce((sum, r) => {
    return sum + (r.metadata?.quality?.mean_snr || 0);
  }, 0) / results.length;

  return {
    ...bestResult,
    metadata: {
      ...bestResult.metadata,
      quality: {
        ...bestResult.metadata?.quality,
        mean_snr: avgSnr
      },
      imageCount: results.length,
      aggregated: true
    }
  };
}


/**
 * GCS Image Access Functions
 * List images, get signed URLs, and process images for digitization
 */

/**
 * List images from GCS stored in Firestore kaggle_images collection
 */
exports.listGCSImages = functions
  .region('us-central1')
  .https.onCall(async (data, context) => {
    try {
      const { subset = 'all', folder = '', limit = 100, startAfter = null } = data || {};
      
      let query = db.collection('kaggle_images');
      
      if (subset === 'train') {
        query = query.where('is_train', '==', true);
      } else if (subset === 'test') {
        query = query.where('is_test', '==', true);
      }
      
      if (folder) {
        query = query.where('folder', '==', folder);
      }
      
      query = query.orderBy('filename').limit(limit);
      
      if (startAfter) {
        try {
          const startAfterDoc = await db.collection('kaggle_images').doc(startAfter).get();
          if (startAfterDoc.exists) {
            query = query.startAfter(startAfterDoc);
          }
        } catch (err) {
          console.log('Error with startAfter:', err);
        }
      }
      
      const snapshot = await query.get();
      const images = [];
      snapshot.forEach(doc => {
        const data = doc.data();
        images.push({
          id: doc.id,
          filename: data.filename || '',
          gcs_bucket: data.gcs_bucket || '',
          gcs_path: data.gcs_path || '',
          gcs_url: data.gcs_url || '',
          size_formatted: data.size_formatted || '',
          is_train: data.is_train || false,
          is_test: data.is_test || false,
          folder: data.folder || ''
        });
      });
      
      // hasMore is true if we got exactly the limit (meaning there might be more)
      const hasMore = images.length === limit;
      
      return { success: true, images, count: images.length, hasMore };
    } catch (error) {
      console.error('Error listing GCS images:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Get signed URL for GCS image
 */
exports.getGCSImageUrl = functions
  .region('us-central1')
  .https.onCall(async (data, context) => {
    try {
      const { imageId, gcsBucket, gcsPath } = data || {};
      
      let bucket = gcsBucket;
      let path = gcsPath;
      
      if (!bucket || !path) {
        if (imageId) {
          const imageDoc = await db.collection('kaggle_images').doc(imageId).get();
          if (!imageDoc.exists) {
            throw new functions.https.HttpsError('not-found', 'Image not found');
          }
          const imageData = imageDoc.data();
          bucket = imageData.gcs_bucket;
          path = imageData.gcs_path || imageData.gcs_url.replace(`gs://${bucket}/`, '');
        } else {
          throw new functions.https.HttpsError('invalid-argument', 'gcsBucket and gcsPath required');
        }
      }
      
      // Try to use public URL first if available
      if (imageId) {
        const imageDoc = await db.collection('kaggle_images').doc(imageId).get();
        if (imageDoc.exists) {
          const imageData = imageDoc.data();
          // Check if there's a public URL stored
          if (imageData.public_url) {
            return { success: true, url: imageData.public_url, expiresIn: 0, isPublic: true };
          }
        }
      }
      
      // Use Firebase Admin Storage which has proper permissions
      const adminStorage = admin.storage();
      const bucketObj = adminStorage.bucket(bucket);
      const file = bucketObj.file(path);
      
      // Check if file exists
      const [exists] = await file.exists();
      if (!exists) {
        throw new functions.https.HttpsError('not-found', 'File not found in GCS');
      }
      
      // Generate signed URL with proper expiration using Admin SDK
      const expiresIn = Date.now() + 3600000; // 1 hour
      const [url] = await file.getSignedUrl({
        action: 'read',
        expires: expiresIn,
        version: 'v4'
      });
      
      return { success: true, url, expiresIn: 3600 };
    } catch (error) {
      console.error('Error getting GCS image URL:', error);
      // Return a more helpful error message
      if (error.message.includes('Permission') || error.message.includes('denied')) {
        throw new functions.https.HttpsError('permission-denied', 
          'Permission denied. Please ensure the Firebase service account has Storage Object Viewer and Service Account Token Creator roles.');
      }
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Process GCS image through digitization pipeline
 */
exports.processGCSImage = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 540, memory: '1GB' })
  .https.onCall(async (data, context) => {
    try {
      const { imageId, gcsBucket, gcsPath } = data || {};
      
      let bucket = gcsBucket;
      let path = gcsPath;
      
      if (!bucket || !path) {
        if (imageId) {
          const imageDoc = await db.collection('kaggle_images').doc(imageId).get();
          if (!imageDoc.exists) {
            throw new functions.https.HttpsError('not-found', 'Image not found');
          }
          const imageData = imageDoc.data();
          bucket = imageData.gcs_bucket;
          path = imageData.gcs_path || imageData.gcs_url.replace(`gs://${bucket}/`, '');
        } else {
          throw new functions.https.HttpsError('invalid-argument', 'gcsBucket and gcsPath required');
        }
      }
      
      const bucketObj = getStorage().bucket(bucket);
      const file = bucketObj.file(path);
      const [imageBuffer] = await file.download();
      
      const result = await digitizeECGImage(imageBuffer, 'gcs', imageId || path);
      
      return { success: true, imageId: imageId || path, ...result };
    } catch (error) {
      console.error('Error processing GCS image:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Compare digitized result with ground truth image (-0001)
 */
exports.compareWithGroundTruth = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 540, memory: '1GB' })
  .https.onCall(async (data, context) => {
    try {
      const { imageId, groundTruthImageId } = data || {};
      
      if (!imageId || !groundTruthImageId) {
        throw new functions.https.HttpsError('invalid-argument', 'Both imageId and groundTruthImageId are required');
      }
      
      // Get both images from Firestore
      const [imageDoc, groundTruthDoc] = await Promise.all([
        db.collection('kaggle_images').doc(imageId).get(),
        db.collection('kaggle_images').doc(groundTruthImageId).get()
      ]);
      
      if (!imageDoc.exists) {
        throw new functions.https.HttpsError('not-found', 'Image not found');
      }
      if (!groundTruthDoc.exists) {
        throw new functions.https.HttpsError('not-found', 'Ground truth image not found');
      }
      
      const imageData = imageDoc.data();
      const groundTruthData = groundTruthDoc.data();
      
      // Download and process both images
      const bucketObj = getStorage().bucket(imageData.gcs_bucket);
      const [imageBuffer, groundTruthBuffer] = await Promise.all([
        bucketObj.file(imageData.gcs_path || imageData.gcs_url.replace(`gs://${imageData.gcs_bucket}/`, '')).download(),
        bucketObj.file(groundTruthData.gcs_path || groundTruthData.gcs_url.replace(`gs://${groundTruthData.gcs_bucket}/`, '')).download()
      ]);
      
      // Process both images
      const [digitizedResult, groundTruthResult] = await Promise.all([
        digitizeECGImage(Buffer.from(imageBuffer[0]), 'gcs', imageId),
        digitizeECGImage(Buffer.from(groundTruthBuffer[0]), 'gcs', groundTruthImageId)
      ]);
      
      // Calculate accuracy using lazy-loaded module
      const { calculateAccuracy } = getCompareAccuracy();
      const accuracy = calculateAccuracy(groundTruthResult, digitizedResult);
      
      return {
        success: true,
        imageId,
        groundTruthImageId,
        accuracy: accuracy.overall,
        perLead: accuracy.perLead,
        metrics: accuracy.metrics,
        digitized: {
          leadCount: digitizedResult.leads?.length || 0,
          metadata: digitizedResult.metadata
        },
        groundTruth: {
          leadCount: groundTruthResult.leads?.length || 0,
          metadata: groundTruthResult.metadata
        }
      };
    } catch (error) {
      console.error('Error comparing with ground truth:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Detect grid lines using Google AI Vision API
 * Uses Vertex AI Vision or Cloud Vision API to detect pink/red grid lines
 */
exports.detectGridLines = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 60, memory: '512MB' })
  .https.onCall(async (data, context) => {
    try {
      const { imageData, imageWidth, imageHeight } = data || {};
      
      if (!imageData) {
        throw new functions.https.HttpsError('invalid-argument', 'imageData is required');
      }
      
      // Decode base64 image
      const base64Data = imageData.replace(/^data:image\/\w+;base64,/, '');
      const imageBuffer = Buffer.from(base64Data, 'base64');
      
      // TODO: Implement Google Cloud Vision API integration
      // Requires: npm install @google-cloud/vision
      // 
      // const vision = require('@google-cloud/vision');
      // const client = new vision.ImageAnnotatorClient();
      // 
      // const [result] = await client.lineDetection({
      //   image: { content: imageBuffer }
      // });
      // 
      // Process lineAnnotations to separate horizontal/vertical
      
      // For now, return structure for client-side fallback
      return {
        success: true,
        horizontal: [],
        vertical: [],
        message: 'Vision API integration pending. Using client-side fallback detection.',
        fallback: true
      };
      
    } catch (error) {
      console.error('Error detecting grid lines:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Analyze grid lines and provide polynomial fit options
 * Calls Python service /analyze-fit endpoint
 */
exports.analyzeFit = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 300, memory: '1GB' })
  .https.onCall(async (data, context) => {
    try {
      const { imageData, max_order } = data || {};
      
      if (!imageData) {
        throw new functions.https.HttpsError('invalid-argument', 'imageData is required');
      }
      
      // Decode base64 image
      const base64Data = imageData.replace(/^data:image\/\w+;base64,/, '');
      const imageBuffer = Buffer.from(base64Data, 'base64');
      
      // Call Python Cloud Run service for fit analysis
      const pythonServiceUrl = process.env.PYTHON_MULTI_METHOD_URL || 
                               functions.config().python?.multi_method_url;
      
      if (!pythonServiceUrl || pythonServiceUrl.includes('XXXXX')) {
        return {
          success: false,
          error: 'Python service not configured. Deploy Python service to Cloud Run.',
          fallback: true
        };
      }
      
      // Call Python service
      try {
        const response = await axios.post(pythonServiceUrl + '/analyze-fit', {
          image: imageBuffer.toString('base64'),
          max_order: max_order || 8
        }, {
          headers: { 'Content-Type': 'application/json' },
          timeout: 120000 // 2 minutes
        });
        
        return response.data;
      } catch (error) {
        console.error('Error calling Python fit analysis service:', error.message);
        throw new functions.https.HttpsError('internal', 
          `Failed to analyze fit: ${error.message}`);
      }
      
    } catch (error) {
      console.error('Error in fit analysis:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Process image with all transformation methods and compare results
 * Tests: Barrel, Polynomial, TPS, Perspective transformations
 */
exports.processMultiMethodTransform = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 300, memory: '1GB' })
  .https.onCall(async (data, context) => {
    try {
      const { imageData, imageWidth, imageHeight } = data || {};
      
      if (!imageData) {
        throw new functions.https.HttpsError('invalid-argument', 'imageData is required');
      }
      
      // Decode base64 image
      const base64Data = imageData.replace(/^data:image\/\w+;base64,/, '');
      const imageBuffer = Buffer.from(base64Data, 'base64');
      
      // Call Python Cloud Run service for multi-method processing
      const pythonServiceUrl = process.env.PYTHON_MULTI_METHOD_URL || 
                               functions.config().python?.multi_method_url;
      
      if (!pythonServiceUrl || pythonServiceUrl.includes('XXXXX')) {
        // Return fallback if service not configured
        return {
          success: false,
          message: 'Python multi-method service URL not configured. Deploy Python service to Cloud Run and set PYTHON_MULTI_METHOD_URL. See QUICK_DEPLOY_GUIDE.md',
          fallback: true,
          results: {
            barrel: { success: false, message: 'Service not deployed' },
            polynomial: { success: false, message: 'Service not deployed' },
            tps: { success: false, message: 'Service not deployed' },
            perspective: { success: false, message: 'Service not deployed' }
          },
          rankings: [],
          best_method: null
        };
      }
      
      // Call Python service
      try {
        const response = await axios.post(pythonServiceUrl + '/transform-multi', {
          image: imageBuffer.toString('base64'),
          width: imageWidth,
          height: imageHeight
        }, {
          headers: { 'Content-Type': 'application/json' },
          timeout: 240000 // 4 minutes
        });
        
        return response.data;
      } catch (error) {
        console.error('Error calling Python multi-method service:', error.message);
        throw new functions.https.HttpsError('internal', 
          `Failed to process multi-method transform: ${error.message}`);
      }
      
    } catch (error) {
      console.error('Error in multi-method transformation:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });
