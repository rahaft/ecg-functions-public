/**
 * Kaggle API Integration for Firebase Functions
 * Fetches images from Kaggle competitions
 */

const functions = require('firebase-functions');
const admin = require('firebase-admin');
const axios = require('axios');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

/**
 * Get images from Kaggle competition
 * This function will use Kaggle API to list and fetch competition images
 */
exports.getKaggleImages = functions
  .region('us-central1')
  .https.onCall(async (data, context) => {
    try {
      const { competition = 'physionet-ecg-image-digitization', subset = 'train' } = data;

      // For now, return structure that indicates images can be loaded
      // Full implementation requires Kaggle API setup on Cloud Functions
      
      // Option 1: Use Kaggle Python client via subprocess (requires Kaggle package installed)
      // Option 2: Use Kaggle REST API directly (requires API token in environment)
      
      const kaggleApiToken = process.env.KAGGLE_API_TOKEN || 
                            functions.config().kaggle?.api_token;
      
      if (!kaggleApiToken) {
        return {
          success: false,
          images: [],
          message: 'Kaggle API token not configured. Set KAGGLE_API_TOKEN environment variable or use functions config.'
        };
      }

      // Use Kaggle REST API to list competition files
      const competitionFiles = await fetchKaggleCompetitionFiles(competition, kaggleApiToken);
      
      // Filter image files
      const imageFiles = competitionFiles.filter(file => 
        /\.(jpg|jpeg|png|tif|tiff)$/i.test(file.name)
      );

      // Filter by subset if specified
      let filteredImages = imageFiles;
      if (subset !== 'all') {
        filteredImages = imageFiles.filter(file => 
          file.name.toLowerCase().includes(subset.toLowerCase())
        );
      }

      // Format for frontend
      const images = filteredImages.map(file => ({
        id: file.name.replace(/[^a-zA-Z0-9]/g, '_'),
        name: file.name,
        url: `kaggle://${competition}/${file.name}`, // Placeholder - actual URLs need to be generated
        size: file.size,
        kaggleUrl: file.downloadUrl || null,
        competition: competition
      }));

      return {
        success: true,
        images: images.slice(0, 100), // Limit to 100 for now
        total: filteredImages.length,
        message: `Found ${filteredImages.length} images in ${competition} (${subset})`
      };

    } catch (error) {
      console.error('Error fetching Kaggle images:', error);
      return {
        success: false,
        images: [],
        message: `Error: ${error.message}. Make sure Kaggle API token is configured.`
      };
    }
  });

/**
 * Fetch competition files using Kaggle REST API
 */
async function fetchKaggleCompetitionFiles(competitionName, apiToken) {
  try {
    // Kaggle REST API endpoint for competition files
    const url = `https://www.kaggle.com/api/v1/competitions/data/list/${competitionName}`;
    
    const response = await axios.get(url, {
      headers: {
        'Authorization': `Bearer ${apiToken}`,
        'Content-Type': 'application/json'
      }
    });

    return response.data || [];
  } catch (error) {
    // If REST API fails, try alternative method
    console.log('REST API failed, trying alternative method:', error.message);
    
    // Alternative: Return structure for manual setup
    return [];
  }
}

/**
 * Download a specific image from Kaggle
 * Returns the image data as base64 or download URL
 */
exports.downloadKaggleImage = functions
  .region('us-central1')
  .https.onCall(async (data, context) => {
    try {
      const { competition, fileName } = data;

      if (!competition || !fileName) {
        throw new functions.https.HttpsError('invalid-argument', 'Competition and fileName required');
      }

      // This would download the image from Kaggle
      // For now, return structure that indicates download URL is needed
      
      return {
        success: true,
        imageUrl: `https://kaggle.com/datasets/${competition}/download/${fileName}`,
        message: 'Image download URL generated. Actual download requires Kaggle API client setup.'
      };

    } catch (error) {
      console.error('Error downloading Kaggle image:', error);
      throw new functions.https.HttpsError('internal', error.message);
    }
  });
