# Polynomial Fit Analysis System

## Overview

The fit analysis system tests multiple polynomial orders against detected grid lines to find the best transformation for correcting image distortion.

## How It Works

### 1. Grid Line Detection
First, horizontal and vertical grid lines are detected in the ECG image using color-based detection (pink/red grid).

### 2. Polynomial Fitting
Each detected line is fit with polynomials of orders 1-8:

| Order | Name | Formula | Use Case |
|-------|------|---------|----------|
| 1 | Linear | y = mx + b | Perfect straight lines |
| 2 | Quadratic | y = ax² + bx + c | Barrel/pincushion distortion |
| 3 | Cubic | y = ax³ + bx² + cx + d | Asymmetric distortion |
| 4 | Quartic | y = ax⁴ + ... | Complex curves |
| 5+ | Higher | y = axⁿ + ... | Wiggly/wavy distortions |

### 3. Metrics Calculated

For each polynomial order, we calculate:

| Metric | Description |
|--------|-------------|
| **R²** | Coefficient of determination (1.0 = perfect fit) |
| **RMSE** | Root mean square error in pixels |
| **MAE** | Mean absolute error in pixels |
| **Max Deviation** | Largest point-to-fit distance |
| **Deviation Histogram** | Distribution of errors |

### 4. Extrema Classification

Lines are classified by the number of local minima/maxima:

| Type | Description | Example |
|------|-------------|---------|
| **none** | Monotonic, no turning points | Straight or simple curve |
| **single** | One minimum or maximum | Barrel distortion |
| **multiple** | Many turning points | Wavy/wiggly scan artifacts |

### 5. Categories

| Category | Meaning |
|----------|---------|
| **straight** | Lines are already straight (R² ≈ 1.0 for linear) |
| **simple_curve** | Single curve (barrel/pincushion) |
| **wiggly** | Multiple curves (scan artifacts) |

## UI Menu Output

The system generates a menu like this:

```
📊 FIT OPTIONS MENU:
─────────────────────────────────────────────────────────────
1. Linear (y = mx + b)
   Combined R²: 0.950000  |  Avg Deviation: 2.500px
   Horizontal R²: 0.95  |  Vertical R²: 0.95
   Perfect fit points: 15%
   Category: needs_correction

2. Quadratic (y = ax² + bx + c) ⭐ RECOMMENDED
   Combined R²: 0.999500  |  Avg Deviation: 0.100px
   Horizontal R²: 0.9995  |  Vertical R²: 0.9995
   Perfect fit points: 92%
   Category: simple_curve  |  Extrema: single

3. Cubic (y = ax³ + bx² + cx + d)
   Combined R²: 0.999600  |  Avg Deviation: 0.095px
   Horizontal R²: 0.9996  |  Vertical R²: 0.9996
   Perfect fit points: 93%
   Category: simple_curve

... (orders 4-8)
```

## API Endpoint

### POST /analyze-fit

**Request:**
```json
{
    "horizontal_lines": [
        [[0, 50], [10, 50.5], [20, 51.2], ...],
        [[0, 100], [10, 100.3], [20, 101.1], ...]
    ],
    "vertical_lines": [
        [[50, 0], [50.5, 10], [51.2, 20], ...],
        [[100, 0], [100.3, 10], [101.1, 20], ...]
    ],
    "max_order": 6
}
```

**Response:**
```json
{
    "success": true,
    "fits": [
        {
            "name": "Linear",
            "order": 1,
            "formula": "y = mx + b",
            "combined_r2": 0.95,
            "horizontal_r2": 0.95,
            "vertical_r2": 0.95,
            "avg_deviation_px": 2.5,
            "max_deviation_px": 5.2,
            "accuracy_stats": {
                "perfect_fit_points": 15,
                "under_half_px": 25,
                "under_1px": 40,
                "total_points": 100,
                "percent_perfect": 15.0,
                "percent_under_half_px": 25.0,
                "percent_under_1px": 40.0
            },
            "extrema_type": "none",
            "num_extrema": 0,
            "is_monotonic": true,
            "recommended": false,
            "category": "needs_correction"
        },
        {
            "name": "Quadratic (Barrel)",
            "order": 2,
            "formula": "y = ax² + bx + c",
            "combined_r2": 0.9995,
            "recommended": true,
            "category": "simple_curve",
            "extrema_type": "single",
            ...
        }
    ],
    "best_fit": { ... },
    "summary": {
        "lines_analyzed": {"horizontal": 10, "vertical": 10, "total": 20},
        "linear_fit_perfect": false,
        "best_order": 2,
        "best_r_squared": 0.9995,
        "recommendation": "Apply Barrel/Pincushion correction (quadratic)",
        "transform_type": "barrel"
    }
}
```

## Implementation Files

| File | Purpose |
|------|---------|
| `transformers/polynomial_fitter.py` | Core polynomial fitting logic |
| `transformers/fit_analyzer.py` | Aggregates results for UI menu |
| `main.py` | Flask endpoint `/analyze-fit` |

## Deployment

After adding these files, redeploy:

```bash
# In Cloud Shell
cd ~/ecg-functions-public
git pull origin main
cd functions_python
gcloud builds submit --tag gcr.io/hv-ecg/ecg-multi-method
gcloud run deploy ecg-multi-method --image gcr.io/hv-ecg/ecg-multi-method --platform managed --region us-central1 --allow-unauthenticated --memory 2Gi
```

## Perfect Fit Goal

The goal is to find the transformation that achieves:
- **R² = 1.0** for both horizontal and vertical lines
- **100% of points with 0 deviation**
- **Relative grid spacing preserved** (equal distances between lines)

If linear fit achieves R² = 1.0, no transformation is needed.
If quadratic achieves it, apply barrel correction.
If higher orders are needed, the image has more complex distortion.
