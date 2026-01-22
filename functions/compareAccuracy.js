/**
 * Accuracy Comparison Module
 * Compares digitized ECG images against ground truth (-0001 images)
 */

/**
 * Calculate accuracy score between two digitized ECG results
 * @param {Object} groundTruth - Ground truth result (from -0001 image)
 * @param {Object} digitized - Digitized result to compare
 * @returns {Object} Accuracy metrics
 */
function calculateAccuracy(groundTruth, digitized) {
  if (!groundTruth.leads || !digitized.leads) {
    return {
      overall: 0,
      perLead: {},
      error: 'Missing lead data'
    };
  }

  const leadNames = groundTruth.leads.map(l => l.name);
  const perLeadScores = {};
  let totalScore = 0;
  let validLeads = 0;

  leadNames.forEach(leadName => {
    const gtLead = groundTruth.leads.find(l => l.name === leadName);
    const digLead = digitized.leads.find(l => l.name === leadName);

    if (!gtLead || !digLead || !gtLead.values || !digLead.values) {
      perLeadScores[leadName] = 0;
      return;
    }

    // Normalize arrays to same length
    const minLength = Math.min(gtLead.values.length, digLead.values.length);
    const gtValues = gtLead.values.slice(0, minLength);
    const digValues = digLead.values.slice(0, minLength);

    // Calculate correlation coefficient
    const correlation = calculateCorrelation(gtValues, digValues);
    
    // Calculate mean squared error (normalized)
    const mse = calculateMSE(gtValues, digValues);
    const maxAmplitude = Math.max(...gtValues.map(Math.abs));
    const normalizedMSE = maxAmplitude > 0 ? mse / (maxAmplitude * maxAmplitude) : 0;
    
    // Calculate structural similarity index (simplified)
    const ssim = calculateSSIM(gtValues, digValues);
    
    // Combined score: weighted average
    // Correlation: 40%, (1 - normalizedMSE): 30%, SSIM: 30%
    const score = (
      correlation * 0.4 +
      (1 - Math.min(normalizedMSE, 1)) * 0.3 +
      ssim * 0.3
    ) * 100;

    perLeadScores[leadName] = Math.max(0, Math.min(100, score));
    totalScore += perLeadScores[leadName];
    validLeads++;
  });

  const overallScore = validLeads > 0 ? totalScore / validLeads : 0;

  return {
    overall: overallScore,
    perLead: perLeadScores,
    metrics: {
      correlation: calculateOverallCorrelation(groundTruth, digitized),
      mse: calculateOverallMSE(groundTruth, digitized),
      ssim: calculateOverallSSIM(groundTruth, digitized)
    }
  };
}

/**
 * Calculate Pearson correlation coefficient
 */
function calculateCorrelation(x, y) {
  if (x.length !== y.length || x.length === 0) return 0;

  const n = x.length;
  const meanX = x.reduce((a, b) => a + b, 0) / n;
  const meanY = y.reduce((a, b) => a + b, 0) / n;

  let numerator = 0;
  let sumSqX = 0;
  let sumSqY = 0;

  for (let i = 0; i < n; i++) {
    const dx = x[i] - meanX;
    const dy = y[i] - meanY;
    numerator += dx * dy;
    sumSqX += dx * dx;
    sumSqY += dy * dy;
  }

  const denominator = Math.sqrt(sumSqX * sumSqY);
  return denominator > 0 ? numerator / denominator : 0;
}

/**
 * Calculate Mean Squared Error
 */
function calculateMSE(x, y) {
  if (x.length !== y.length || x.length === 0) return Infinity;
  
  let sumSqError = 0;
  for (let i = 0; i < x.length; i++) {
    sumSqError += Math.pow(x[i] - y[i], 2);
  }
  
  return sumSqError / x.length;
}

/**
 * Calculate Structural Similarity Index (simplified)
 */
function calculateSSIM(x, y) {
  if (x.length !== y.length || x.length === 0) return 0;

  const c1 = 0.01;
  const c2 = 0.03;

  const meanX = x.reduce((a, b) => a + b, 0) / x.length;
  const meanY = y.reduce((a, b) => a + b, 0) / y.length;

  let varX = 0;
  let varY = 0;
  let covXY = 0;

  for (let i = 0; i < x.length; i++) {
    const dx = x[i] - meanX;
    const dy = y[i] - meanY;
    varX += dx * dx;
    varY += dy * dy;
    covXY += dx * dy;
  }

  const n = x.length;
  varX /= n;
  varY /= n;
  covXY /= n;

  const numerator = (2 * meanX * meanY + c1) * (2 * covXY + c2);
  const denominator = (meanX * meanX + meanY * meanY + c1) * (varX + varY + c2);

  return denominator > 0 ? numerator / denominator : 0;
}

/**
 * Calculate overall correlation across all leads
 */
function calculateOverallCorrelation(gt, dig) {
  const allGtValues = [];
  const allDigValues = [];

  gt.leads.forEach(gtLead => {
    const digLead = dig.leads.find(l => l.name === gtLead.name);
    if (digLead && gtLead.values && digLead.values) {
      const minLen = Math.min(gtLead.values.length, digLead.values.length);
      allGtValues.push(...gtLead.values.slice(0, minLen));
      allDigValues.push(...digLead.values.slice(0, minLen));
    }
  });

  return calculateCorrelation(allGtValues, allDigValues);
}

/**
 * Calculate overall MSE across all leads
 */
function calculateOverallMSE(gt, dig) {
  let totalMSE = 0;
  let count = 0;

  gt.leads.forEach(gtLead => {
    const digLead = dig.leads.find(l => l.name === gtLead.name);
    if (digLead && gtLead.values && digLead.values) {
      const minLen = Math.min(gtLead.values.length, digLead.values.length);
      const mse = calculateMSE(
        gtLead.values.slice(0, minLen),
        digLead.values.slice(0, minLen)
      );
      totalMSE += mse;
      count++;
    }
  });

  return count > 0 ? totalMSE / count : Infinity;
}

/**
 * Calculate overall SSIM across all leads
 */
function calculateOverallSSIM(gt, dig) {
  let totalSSIM = 0;
  let count = 0;

  gt.leads.forEach(gtLead => {
    const digLead = dig.leads.find(l => l.name === gtLead.name);
    if (digLead && gtLead.values && digLead.values) {
      const minLen = Math.min(gtLead.values.length, digLead.values.length);
      const ssim = calculateSSIM(
        gtLead.values.slice(0, minLen),
        digLead.values.slice(0, minLen)
      );
      totalSSIM += ssim;
      count++;
    }
  });

  return count > 0 ? totalSSIM / count : 0;
}

module.exports = {
  calculateAccuracy,
  calculateCorrelation,
  calculateMSE,
  calculateSSIM
};
