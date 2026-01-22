# Test Gallery Page on Live Website

## 🚀 Deployment Status

The gallery page is being deployed to Firebase Hosting.

**Live URL:** `https://hv-ecg.web.app/gallery.html`

---

## ✅ What to Test

### 1. **Page Loads**
- Go to: `https://hv-ecg.web.app/gallery.html`
- Should see: "ECG Image Gallery" header
- Should see: "Loading images..." message

### 2. **Images Display**
- Wait for images to load (auto sign-in happens)
- Should see: Gallery grid with ECG images
- Images should be clickable (opens in new tab)

### 3. **Version Footer**
- Scroll to bottom
- Should see: Version info on one line
- **Click anywhere on the version line** → Should copy to clipboard
- **Click "📋 Copy" button** → Should copy to clipboard
- Should see green flash when copied

### 4. **Bulk Testing (Browser Console)**
- Press **F12** to open console
- Wait for images to load
- Run: `quickBulkTest()`
- Should see: Processing messages in console
- Should see: Results with edge detection, color separation, etc.

---

## 🧪 Test Commands (Browser Console)

### Quick Bulk Test
```javascript
quickBulkTest();
```

### Custom Bulk Test
```javascript
bulkTestGallery({
    edge_detection: true,
    color_separation: true,
    grid_detection: true,
    quality_check: true
});
```

### Test Single Image
```javascript
const img = document.querySelector('.gallery-item img');
detectEdges(img, 'canny', true).then(console.log);
```

### Process Batch
```javascript
const images = Array.from(document.querySelectorAll('.gallery-item img')).slice(0, 5);
processBatch(images, {
    edge_detection: true,
    color_separation: true
}).then(console.log);
```

---

## 🔍 What to Check

### ✅ Success Indicators
- [ ] Page loads without errors
- [ ] Images appear in gallery grid
- [ ] Version footer shows correct info
- [ ] Clicking footer copies version info
- [ ] Console shows "Loaded X images"
- [ ] `quickBulkTest()` runs successfully
- [ ] No CORS errors in console
- [ ] No 404 errors for scripts

### ❌ Common Issues

**"No images found"**
- Solution: Upload images from main page first
- Or: Check Firebase Storage has images in `ecg_images/` folder

**CORS Errors**
- Solution: Python service needs CORS enabled (already done)
- Check: `https://ecg-multi-method-101881880910.us-central1.run.app/health`

**"quickBulkTest is not defined"**
- Solution: Refresh page after deployment
- Check: Browser console for script loading errors

**Version info not copying**
- Solution: Check browser console for errors
- Try: Manual copy (select text, Ctrl+C)

---

## 📊 Expected Console Output

**On Page Load:**
```
Firebase initialized successfully
Loaded 10 images
```

**After quickBulkTest():**
```
Processing 10 images...
{success: true, count: 10, results: [...]}
```

---

## 🎯 Quick Test Checklist

1. ✅ Open: `https://hv-ecg.web.app/gallery.html`
2. ✅ Wait for images to load
3. ✅ Check footer is visible
4. ✅ Click footer → Should copy version info
5. ✅ Open console (F12)
6. ✅ Run: `quickBulkTest()`
7. ✅ Check results in console

---

**After deployment completes, test the live site!** 🎉
