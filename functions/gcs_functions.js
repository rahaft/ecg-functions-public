/**
 * Firebase Cloud Functions for GCS Image Access
 * List images, get signed URLs, and process images for digitization
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { Storage } = require('@google-cloud/storage');

// Storage client for GCS
const storage = new Storage({
  projectId: 'hv-ecg'
});

/**
 * List images from GCS stored in Firestore kaggle_images collection
 */
exports.listGCSImages = functions
  .region('us-central1')
  .https.onCall(async (data, context) => {
    try {
      const { subset = 'all', folder = '', limit = 100, startAfter = null } = data || {};
      
      const db = admin.firestore();
      let query = db.collection('kaggle_images');
      
      // Filter by subset (train/test)
      if (subset === 'train') {
        query = query.where('is_train', '==', true);
      } else if (subset === 'test') {
        query = query.where('is_test', '==', true);
      }
      
      // Filter by folder if specified
      if (folder) {
        query = query.where('folder', '==', folder);
      }
      
      // Order by filename for consistent pagination
      query = query.orderBy('filename');
      
      // Pagination
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
      
      query = query.limit(limit);
      
      const snapshot = await query.get();
      
      const images = [];
      snapshot.forEach(doc => {
        const data = doc.data();
        images.push({
          id: doc.id,
          filename: data.filename || '',
          full_path: data.full_path || '',
          gcs_bucket: data.gcs_bucket || '',
          gcs_path: data.gcs_path || '',
          gcs_url: data.gcs_url || '',
          gcs_public_url: data.gcs_public_url || '',
          size: data.size || 0,
          size_formatted: data.size_formatted || '',
          is_train: data.is_train || false,
          is_test: data.is_test || false,
          folder: data.folder || '',
          competition: data.competition || 'physionet-ecg-image-digitization'
        });
      });
      
      return {
        success: true,
        images: images,
        count: images.length,
        hasMore: snapshot.size === limit,
        lastDocId: images.length > 0 ? images[images.length - 1].id : null
      };
      
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
      
      if (!gcsBucket || !gcsPath) {
        // Try to get from Firestore if imageId provided
        if (imageId) {
          const db = admin.firestore();
          const imageDoc = await db.collection('kaggle_images').doc(imageId).get();
          if (!imageDoc.exists) {
            throw new functions.https.HttpsError('not-found', 'Image not found');
          }
          const imageData = imageDoc.data();
          
          // Extract bucket and path
          const bucket = imageData.gcs_bucket;
          const path = imageData.gcs_path || imageData.gcs_url.replace(`gs://${bucket}/`, '');
          
          if (!bucket || !path) {
            throw new functions.https.HttpsError('invalid-argument', 'Missing gcs_bucket or gcs_path in Firestore document');
          }
          
          return await generateSignedUrl(bucket, path);
        }
        throw new functions.https.HttpsError('invalid-argument', 'gcsBucket and gcsPath required');
      }
      
      return await generateSignedUrl(gcsBucket, gcsPath);
      
    } catch (error) {
      console.error('Error getting GCS image URL:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });

/**
 * Helper function to generate signed URL for GCS file
 */
async function generateSignedUrl(bucketName, filePath) {
  try {
    const bucket = storage.bucket(bucketName);
    const file = bucket.file(filePath);
    
    // Check if file exists
    const [exists] = await file.exists();
    if (!exists) {
      throw new Error(`File not found: gs://${bucketName}/${filePath}`);
    }
    
    const [url] = await file.getSignedUrl({
      action: 'read',
      expires: Date.now() + 3600000 // 1 hour
    });
    
    return {
      success: true,
      url: url,
      expiresIn: 3600,
      bucket: bucketName,
      path: filePath
    };
  } catch (error) {
    throw new Error(`Failed to generate signed URL: ${error.message}`);
  }
}

/**
 * Process GCS image through digitization pipeline
 * Downloads image from GCS and processes it
 */
exports.processGCSImage = functions
  .region('us-central1')
  .runWith({ timeoutSeconds: 540, memory: '1GB' })
  .https.onCall(async (data, context) => {
    try {
      const { imageId, gcsBucket, gcsPath } = data || {};
      
      // Get image info from Firestore if imageId provided
      let bucket = gcsBucket;
      let path = gcsPath;
      
      if (!bucket || !path) {
        if (imageId) {
          const db = admin.firestore();
          const imageDoc = await db.collection('kaggle_images').doc(imageId).get();
          if (!imageDoc.exists) {
            throw new functions.https.HttpsError('not-found', 'Image not found');
          }
          const imageData = imageDoc.data();
          bucket = imageData.gcs_bucket;
          path = imageData.gcs_path || imageData.gcs_url.replace(`gs://${bucket}/`, '');
        }
      }
      
      if (!bucket || !path) {
        throw new functions.https.HttpsError('invalid-argument', 'gcsBucket and gcsPath required');
      }
      
      // Download image from GCS
      const gcsBucketObj = storage.bucket(bucket);
      const file = gcsBucketObj.file(path);
      const [imageBuffer] = await file.download();
      
      console.log(`Downloaded image from gs://${bucket}/${path}, size: ${imageBuffer.length} bytes`);
      
      // For now, return structure - actual digitization will be integrated
      // This calls the existing digitizeECGImage function if available
      let result;
      try {
        // Try to call the existing digitization function
        // This would be in the same file or imported
        result = await digitizeECGImage(imageBuffer, 'gcs', imageId || path);
      } catch (digitizationError) {
        console.log('Digitization function not available, returning metadata only:', digitizationError.message);
        // Fallback: return basic metadata
        result = {
          imageId: imageId || path,
          leads: [],
          metadata: {
            imageSize: imageBuffer.length,
            processingDate: new Date().toISOString(),
            gcsBucket: bucket,
            gcsPath: path,
            note: 'Digitization pipeline not yet integrated - returning metadata only'
          }
        };
      }
      
      return {
        success: true,
        imageId: imageId || path,
        ...result
      };
      
    } catch (error) {
      console.error('Error processing GCS image:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });
