# CORS Fix Guide for Transform Tab

## Current Issue

The Transform tab is working, but client-side grid detection is blocked by CORS (Cross-Origin Resource Sharing) when trying to read pixel data from images loaded from GCS.

**Error:** `SecurityError: Failed to execute 'getImageData' on 'CanvasRenderingContext2D': The canvas has been tainted by cross-origin data.`

## Why This Happens

When images are loaded from GCS without proper CORS headers, the browser marks the canvas as "tainted" and prevents reading pixel data for security reasons.

## Solutions

### Solution 1: Server-Side Processing (Recommended) ✅

**Best approach:** Use the Python service to process images server-side, which bypasses CORS entirely.

**Steps:**
1. Deploy Python service to Cloud Run (see `MULTI_METHOD_SETUP.md`)
2. Update Cloud Function to call Python service
3. Images are processed server-side, no CORS issues

**Status:** Python service structure ready, needs deployment

### Solution 2: Configure CORS on GCS Buckets

**Alternative:** Configure CORS headers on GCS buckets to allow client-side access.

**Steps:**
1. Run the CORS configuration script:
   ```bash
   python scripts/configure_gcs_cors.py
   ```

2. Or manually configure in Google Cloud Console:
   - Go to Cloud Storage → Buckets
   - Select bucket (e.g., `ecg-competition-data-1`)
   - Click "Permissions" tab
   - Add CORS configuration:
   ```json
   [
     {
       "origin": ["https://hv-ecg.web.app", "http://localhost:*"],
       "method": ["GET", "HEAD"],
       "responseHeader": ["Content-Type", "Access-Control-Allow-Origin"],
       "maxAgeSeconds": 3600
     }
   ]
   ```

3. Ensure images are loaded with `crossOrigin = 'anonymous'` (already done in code)

**Status:** CORS script exists, may need to re-run

### Solution 3: Use Cloud Function Proxy

**Workaround:** Create a Cloud Function that fetches images and returns them with CORS headers.

**Implementation:**
- Create `getImageWithCORS` Cloud Function
- Function fetches image from GCS
- Returns image data with proper CORS headers
- Frontend uses this URL instead of direct GCS URL

**Status:** Not implemented (Solution 1 is preferred)

## Current Workaround

The code now:
1. ✅ Sets `crossOrigin = 'anonymous'` on images
2. ✅ Catches CORS errors gracefully
3. ✅ Shows helpful error messages
4. ✅ Falls back to server-side processing message

## What Works Now

- ✅ Transform tab is visible
- ✅ UI controls work
- ✅ Method info panel works
- ✅ Error handling for CORS
- ⚠️ Client-side detection blocked by CORS
- ✅ Server-side processing ready (needs deployment)

## Next Steps

1. **Deploy Python Service** (Best solution)
   - Follow `MULTI_METHOD_SETUP.md`
   - Deploy to Cloud Run
   - Update Cloud Function URL
   - Full functionality without CORS issues

2. **Or Re-configure CORS** (Alternative)
   - Run `python scripts/configure_gcs_cors.py`
   - Verify CORS headers are set
   - Test client-side detection

## Testing

After fixing CORS or deploying Python service:

1. Open an image in comparison modal
2. Click "Transform" tab
3. Click "Detect & Transform"
4. Should see:
   - Grid lines detected
   - Transformation applied
   - Original and transformed images
   - Quality metrics

## Files Modified

- `public/gallery.html` - Added CORS error handling
- `scripts/configure_gcs_cors.py` - CORS configuration script (exists)

## References

- `MULTI_METHOD_SETUP.md` - Python service deployment
- `FIX_GCS_PERMISSIONS.md` - GCS permissions guide
- `scripts/configure_gcs_cors.py` - CORS configuration script
