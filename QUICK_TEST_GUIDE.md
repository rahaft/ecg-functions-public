# Quick Test Guide - Transformation Methods

## 🚀 Fastest Way to Test (Web UI)

### 1. Open Gallery
👉 **https://hv-ecg.web.app/gallery.html**

### 2. Click Any Image
- Click on any image card in the gallery
- This opens the **Comparison Modal**

### 3. Go to Transform Tab
- Look for **3 tabs** at the top: `Compare | Algorithm | Transform`
- Click **"Transform"** tab

### 4. Test Single Method (Barrel)
- Click **"🔍 Detect & Transform"** button
- Wait a few seconds
- You'll see:
  - ✅ Original image with green grid lines detected
  - ✅ Transformed/corrected image
  - ✅ Quality metrics (R², RMSE)

### 5. Test All Methods
- Click **"🔄 Process All Methods"** button
- Currently shows: "Integration pending" (Python service not deployed yet)
- Once Python service is deployed, you'll see:
  - 4 method comparison cards
  - Rankings table
  - Best method highlighted 🏆

---

## 🐍 Test Locally with Python

### Quick Test (5 minutes)

1. **Navigate to Python directory:**
   ```bash
   cd functions_python
   ```

2. **Test with sample image:**
   ```bash
   python test_transformations.py --sample
   ```
   This creates a test image and runs all methods.

3. **Or test with your own image:**
   ```bash
   python test_transformations.py path/to/your/ecg_image.png
   ```

4. **View results:**
   - Rankings table in terminal
   - Transformed images saved as:
     - `transformed_barrel.png`
     - `transformed_polynomial.png`
     - `best_transformation.png`

---

## 📊 What You'll See

### In Web UI (Transform Tab)

```
┌─────────────────────────────────────────┐
│  🔄 Grid Transformation (v2)             │
├─────────────────────────────────────────┤
│  [🔍 Detect & Transform]               │
│  [🔄 Process All Methods]               │
│  [Reset] [Apply Best Transformation]   │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐  ┌─────────────┐     │
│  │ Original    │  │ Transformed │     │
│  │ with Lines  │  │ Grid        │     │
│  └─────────────┘  └─────────────┘     │
│                                         │
│  Method Comparison Results:             │
│  ┌──────────┐ ┌──────────┐             │
│  │ Barrel   │ │Polynomial│             │
│  │ R²: 0.95 │ │ R²: 0.92 │             │
│  │ 🏆 Best  │ │          │             │
│  └──────────┘ └──────────┘             │
│                                         │
│  Rankings Table:                        │
│  Rank | Method    | Score | R² | RMSE │
│  1    | barrel    | 0.92  |0.95| 2.3  │
│  2    | polynomial| 0.88  |0.92| 3.1  │
└─────────────────────────────────────────┘
```

### In Python Terminal

```
============================================================
ECG TRANSFORMATION TEST
============================================================

Image: sample_ecg.png
Size: 800x600 pixels

Processing with all transformation methods...

============================================================
RESULTS
============================================================

Total processing time: 4.52 seconds
Methods tested: barrel, polynomial

🏆 BEST METHOD: BARREL

------------------------------------------------------------
RANKINGS (sorted by combined score)
------------------------------------------------------------
Rank   Method          Score    R²       RMSE       Quality      Time    
------------------------------------------------------------
🏆     barrel          0.920    0.950    2.30       excellent    1.20s
2.     polynomial      0.880    0.920    3.10       good         1.15s

------------------------------------------------------------
DETAILED RESULTS
------------------------------------------------------------

BARREL:
  ✅ Success
  R²: 0.950
  RMSE: 2.30 pixels
  Quality: excellent
  Processing Time: 1.20s
  💾 Saved: transformed_barrel.png

POLYNOMIAL:
  ✅ Success
  R²: 0.920
  RMSE: 3.10 pixels
  Quality: good
  Processing Time: 1.15s
  💾 Saved: transformed_polynomial.png

✅ Best transformation saved to: best_transformation.png
```

---

## 🎯 What Each Method Does

### 1. Barrel Distortion ✅ (Working)
- **What it fixes**: Camera lens distortion, barrel/pincushion effects
- **Best for**: Photos taken with phone cameras
- **Status**: Fully implemented

### 2. Polynomial Transform 🚧 (Partial)
- **What it fixes**: Smooth warping, curved paper
- **Best for**: Scanned images with slight warping
- **Status**: Structure ready, warp implementation pending

### 3. TPS (Thin Plate Spline) ⏳ (Not yet)
- **What it fixes**: Complex distortions, crumpled paper
- **Best for**: Heavily warped or folded ECG paper
- **Status**: To be implemented

### 4. Perspective Transform ⏳ (Not yet)
- **What it fixes**: Angled photos, perspective distortion
- **Best for**: Photos taken at an angle
- **Status**: To be implemented

---

## 📈 Understanding Quality Scores

### R² (R-squared)
- **Range**: 0.0 to 1.0
- **Meaning**: How well transformation fits ideal grid
- **Excellent**: > 0.95
- **Good**: > 0.90
- **Fair**: > 0.85
- **Poor**: < 0.85

### RMSE (Root Mean Square Error)
- **Unit**: Pixels
- **Meaning**: Average distance error
- **Excellent**: < 2px
- **Good**: < 5px
- **Fair**: < 10px
- **Poor**: > 10px

### Combined Score
- **Range**: 0.0 to 1.0
- **Formula**: 30% geometric + 70% signal quality
- **Higher is better**

---

## 🔧 Troubleshooting

### "Integration pending" in Web UI
- **Why**: Python service not deployed to Cloud Run
- **Solution**: Test locally with Python, or deploy service (see MULTI_METHOD_SETUP.md)

### "No module named 'transformers'"
- **Why**: Python path issue
- **Solution**: 
  ```bash
  cd functions_python
  export PYTHONPATH=$PWD:$PYTHONPATH
  python test_transformations.py --sample
  ```

### Images not loading in gallery
- **Why**: GCS permissions
- **Solution**: Check bucket permissions (see FIX_GCS_PERMISSIONS.md)

### Only barrel method works
- **Why**: Other methods not fully implemented yet
- **Status**: This is expected - barrel is complete, others are in progress

---

## 📝 Next Steps

1. ✅ **Test Barrel Method** - Works now!
2. ⏳ **Deploy Python Service** - For full multi-method comparison
3. ⏳ **Complete Other Methods** - Finish polynomial, add TPS and perspective
4. ⏳ **Compare Results** - See which works best for your images

---

## 🎓 Learning Resources

- **Full Guide**: See `HOW_TO_TEST_TRANSFORMATIONS.md`
- **Setup**: See `MULTI_METHOD_SETUP.md`
- **Implementation**: See `MULTI_METHOD_IMPLEMENTATION.md`
- **Task List**: See `transformation_task_list.md`

---

## 💡 Pro Tips

1. **Start with Barrel** - It's fully working and handles most common distortions
2. **Compare visually** - Look at the transformed images, not just scores
3. **Test multiple images** - Different images may need different methods
4. **Check RMSE** - Lower is better for grid alignment
5. **Use best method** - The system automatically selects the highest score

---

**Ready to test?** Go to: https://hv-ecg.web.app/gallery.html → Click image → Transform tab → "Detect & Transform"
