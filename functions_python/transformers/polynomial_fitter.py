"""
Polynomial Fitting System for ECG Grid Line Analysis

Fits multiple polynomial orders to detected grid lines and provides
comprehensive metrics for selecting the best transformation.

Features:
- Multiple polynomial orders (1st through 8th)
- Classification by extrema (single vs multiple minima/maxima)
- Comprehensive metrics (R², RMSE, MAE, deviation histogram)
- Automatic best-fit selection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import warnings


@dataclass
class FitResult:
    """Result of a polynomial fit"""
    order: int
    coefficients: np.ndarray
    r_squared: float
    rmse: float
    mae: float  # Mean Absolute Error
    max_deviation: float
    deviation_histogram: Dict[str, int]  # e.g., {"<0.5px": 95, "0.5-1px": 3, ">1px": 2}
    num_extrema: int  # Number of local minima/maxima within the line
    extrema_type: str  # "none", "single", "multiple"
    is_monotonic: bool
    fitted_values: np.ndarray
    residuals: np.ndarray
    
    def to_dict(self) -> Dict:
        return {
            'order': self.order,
            'coefficients': self.coefficients.tolist(),
            'r_squared': round(self.r_squared, 6),
            'rmse': round(self.rmse, 4),
            'mae': round(self.mae, 4),
            'max_deviation': round(self.max_deviation, 4),
            'deviation_histogram': self.deviation_histogram,
            'num_extrema': self.num_extrema,
            'extrema_type': self.extrema_type,
            'is_monotonic': self.is_monotonic
        }


@dataclass
class LineFitAnalysis:
    """Complete analysis of a single line across all polynomial orders"""
    line_id: int
    line_type: str  # "horizontal" or "vertical"
    points: np.ndarray
    fits: List[FitResult]
    best_fit_order: int
    best_r_squared: float
    is_perfectly_straight: bool  # R² = 1.0 for linear fit
    recommended_order: int
    
    def to_dict(self) -> Dict:
        return {
            'line_id': self.line_id,
            'line_type': self.line_type,
            'num_points': len(self.points),
            'fits': [f.to_dict() for f in self.fits],
            'best_fit_order': self.best_fit_order,
            'best_r_squared': round(self.best_r_squared, 6),
            'is_perfectly_straight': self.is_perfectly_straight,
            'recommended_order': self.recommended_order
        }


class PolynomialFitter:
    """
    Fits multiple polynomial orders to grid lines and analyzes results.
    """
    
    def __init__(self, max_order: int = 8, perfect_threshold: float = 0.9999):
        """
        Args:
            max_order: Maximum polynomial order to try (default 8)
            perfect_threshold: R² threshold for "perfect" fit (default 0.9999)
        """
        self.max_order = max_order
        self.perfect_threshold = perfect_threshold
        
    def fit_line(self, points: np.ndarray, line_id: int = 0, 
                 line_type: str = "horizontal") -> LineFitAnalysis:
        """
        Fit all polynomial orders to a single line.
        
        Args:
            points: Nx2 array of (x, y) coordinates
            line_id: Identifier for the line
            line_type: "horizontal" or "vertical"
            
        Returns:
            LineFitAnalysis with all fit results
        """
        if len(points) < 3:
            raise ValueError("Need at least 3 points to fit")
        
        # For horizontal lines, fit y = f(x)
        # For vertical lines, fit x = f(y)
        if line_type == "horizontal":
            x = points[:, 0]
            y = points[:, 1]
        else:
            x = points[:, 1]  # Use y as independent variable
            y = points[:, 0]  # Fit x values
        
        # Sort by independent variable
        sort_idx = np.argsort(x)
        x = x[sort_idx]
        y = y[sort_idx]
        
        fits = []
        best_r2 = -np.inf
        best_order = 1
        
        for order in range(1, min(self.max_order + 1, len(points))):
            try:
                fit_result = self._fit_polynomial(x, y, order)
                fits.append(fit_result)
                
                if fit_result.r_squared > best_r2:
                    best_r2 = fit_result.r_squared
                    best_order = order
                    
            except Exception as e:
                warnings.warn(f"Failed to fit order {order}: {e}")
                continue
        
        # Check if line is perfectly straight
        is_straight = fits[0].r_squared >= self.perfect_threshold if fits else False
        
        # Recommend order based on complexity vs. improvement
        recommended = self._recommend_order(fits)
        
        return LineFitAnalysis(
            line_id=line_id,
            line_type=line_type,
            points=points,
            fits=fits,
            best_fit_order=best_order,
            best_r_squared=best_r2,
            is_perfectly_straight=is_straight,
            recommended_order=recommended
        )
    
    def _fit_polynomial(self, x: np.ndarray, y: np.ndarray, 
                        order: int) -> FitResult:
        """Fit a single polynomial order and compute metrics."""
        
        # Fit polynomial
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', np.RankWarning)
            coeffs = np.polyfit(x, y, order)
        
        # Compute fitted values
        fitted = np.polyval(coeffs, x)
        
        # Residuals
        residuals = y - fitted
        
        # R² (coefficient of determination)
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
        
        # RMSE
        rmse = np.sqrt(np.mean(residuals ** 2))
        
        # MAE (Mean Absolute Error)
        mae = np.mean(np.abs(residuals))
        
        # Max deviation
        max_dev = np.max(np.abs(residuals))
        
        # Deviation histogram
        abs_residuals = np.abs(residuals)
        histogram = {
            "perfect (0)": int(np.sum(abs_residuals < 0.01)),
            "<0.5px": int(np.sum((abs_residuals >= 0.01) & (abs_residuals < 0.5))),
            "0.5-1px": int(np.sum((abs_residuals >= 0.5) & (abs_residuals < 1.0))),
            "1-2px": int(np.sum((abs_residuals >= 1.0) & (abs_residuals < 2.0))),
            ">2px": int(np.sum(abs_residuals >= 2.0))
        }
        
        # Find extrema (local minima/maxima) in the fitted curve
        num_extrema, extrema_type = self._count_extrema(coeffs, x)
        
        # Check if monotonic
        derivative = np.polyder(coeffs)
        deriv_values = np.polyval(derivative, x)
        is_monotonic = np.all(deriv_values >= 0) or np.all(deriv_values <= 0)
        
        return FitResult(
            order=order,
            coefficients=coeffs,
            r_squared=r_squared,
            rmse=rmse,
            mae=mae,
            max_deviation=max_dev,
            deviation_histogram=histogram,
            num_extrema=num_extrema,
            extrema_type=extrema_type,
            is_monotonic=is_monotonic,
            fitted_values=fitted,
            residuals=residuals
        )
    
    def _count_extrema(self, coeffs: np.ndarray, x: np.ndarray) -> Tuple[int, str]:
        """Count local minima/maxima within the x range."""
        
        if len(coeffs) <= 2:  # Linear or constant
            return 0, "none"
        
        # Find derivative roots (critical points)
        derivative = np.polyder(coeffs)
        
        try:
            # For polynomial, critical points are roots of derivative
            critical_points = np.roots(derivative)
            
            # Filter to real roots within x range
            x_min, x_max = x.min(), x.max()
            real_critical = []
            for cp in critical_points:
                if np.isreal(cp):
                    cp_real = np.real(cp)
                    if x_min < cp_real < x_max:
                        real_critical.append(cp_real)
            
            num_extrema = len(real_critical)
            
            if num_extrema == 0:
                extrema_type = "none"
            elif num_extrema == 1:
                extrema_type = "single"
            else:
                extrema_type = "multiple"
                
            return num_extrema, extrema_type
            
        except Exception:
            return 0, "unknown"
    
    def _recommend_order(self, fits: List[FitResult]) -> int:
        """
        Recommend the best polynomial order using the elbow method.
        
        Balance between fit quality and complexity:
        - Prefer lower orders if R² improvement is minimal
        - Prefer higher orders only if significant improvement
        """
        if not fits:
            return 1
        
        if len(fits) == 1:
            return fits[0].order
        
        # If linear fit is perfect, recommend it
        if fits[0].r_squared >= self.perfect_threshold:
            return 1
        
        # Find elbow point where improvement becomes marginal
        improvement_threshold = 0.001  # 0.1% improvement threshold
        
        recommended = fits[0].order
        prev_r2 = fits[0].r_squared
        
        for fit in fits[1:]:
            improvement = fit.r_squared - prev_r2
            
            if improvement > improvement_threshold:
                recommended = fit.order
                prev_r2 = fit.r_squared
            else:
                # Improvement is marginal, stop here
                break
        
        return recommended
    
    def analyze_all_lines(self, horizontal_lines: List[np.ndarray],
                          vertical_lines: List[np.ndarray]) -> Dict:
        """
        Analyze all grid lines and provide comprehensive fit report.
        
        Args:
            horizontal_lines: List of Nx2 arrays for horizontal lines
            vertical_lines: List of Nx2 arrays for vertical lines
            
        Returns:
            Complete analysis report
        """
        h_analyses = []
        v_analyses = []
        
        # Analyze horizontal lines
        for i, points in enumerate(horizontal_lines):
            if len(points) >= 3:
                analysis = self.fit_line(points, line_id=i, line_type="horizontal")
                h_analyses.append(analysis)
        
        # Analyze vertical lines
        for i, points in enumerate(vertical_lines):
            if len(points) >= 3:
                analysis = self.fit_line(points, line_id=i, line_type="vertical")
                v_analyses.append(analysis)
        
        # Aggregate statistics
        report = self._generate_report(h_analyses, v_analyses)
        
        return report
    
    def _generate_report(self, h_analyses: List[LineFitAnalysis],
                         v_analyses: List[LineFitAnalysis]) -> Dict:
        """Generate comprehensive fit report."""
        
        def summarize_lines(analyses: List[LineFitAnalysis], line_type: str) -> Dict:
            if not analyses:
                return {"count": 0, "message": f"No {line_type} lines detected"}
            
            # Check if all lines are perfectly straight with linear fit
            all_straight = all(a.is_perfectly_straight for a in analyses)
            
            # Average R² per order
            order_stats = {}
            for order in range(1, self.max_order + 1):
                r2_values = []
                for a in analyses:
                    for f in a.fits:
                        if f.order == order:
                            r2_values.append(f.r_squared)
                            break
                
                if r2_values:
                    order_stats[f"order_{order}"] = {
                        "avg_r_squared": round(np.mean(r2_values), 6),
                        "min_r_squared": round(np.min(r2_values), 6),
                        "max_r_squared": round(np.max(r2_values), 6),
                        "all_perfect": all(r2 >= self.perfect_threshold for r2 in r2_values)
                    }
            
            # Recommended order distribution
            recommended_orders = [a.recommended_order for a in analyses]
            order_counts = {i: recommended_orders.count(i) for i in set(recommended_orders)}
            
            # Extrema distribution
            extrema_types = {"none": 0, "single": 0, "multiple": 0}
            for a in analyses:
                # Use the recommended fit's extrema type
                for f in a.fits:
                    if f.order == a.recommended_order:
                        if f.extrema_type in extrema_types:
                            extrema_types[f.extrema_type] += 1
                        break
            
            return {
                "count": len(analyses),
                "all_perfectly_straight": all_straight,
                "order_statistics": order_stats,
                "recommended_order_distribution": order_counts,
                "extrema_distribution": extrema_types,
                "lines": [a.to_dict() for a in analyses]
            }
        
        horizontal_summary = summarize_lines(h_analyses, "horizontal")
        vertical_summary = summarize_lines(v_analyses, "vertical")
        
        # Overall recommendation
        all_h_straight = horizontal_summary.get("all_perfectly_straight", False)
        all_v_straight = vertical_summary.get("all_perfectly_straight", False)
        
        if all_h_straight and all_v_straight:
            overall_recommendation = "LINEAR - All lines are perfectly straight (R²=1)"
            transformation_needed = "none"
        elif all_h_straight or all_v_straight:
            overall_recommendation = "PARTIAL - One direction is straight, other needs correction"
            transformation_needed = "single_axis"
        else:
            # Find most common recommended order
            all_recommendations = (
                [a.recommended_order for a in h_analyses] +
                [a.recommended_order for a in v_analyses]
            )
            if all_recommendations:
                most_common = max(set(all_recommendations), key=all_recommendations.count)
                overall_recommendation = f"ORDER_{most_common} - Polynomial correction recommended"
                transformation_needed = f"polynomial_order_{most_common}"
            else:
                overall_recommendation = "UNKNOWN - Insufficient data"
                transformation_needed = "unknown"
        
        return {
            "horizontal": horizontal_summary,
            "vertical": vertical_summary,
            "overall_recommendation": overall_recommendation,
            "transformation_needed": transformation_needed,
            "perfect_fit_achieved": all_h_straight and all_v_straight
        }


def demo_polynomial_fitting():
    """Demonstrate polynomial fitting with sample data."""
    
    # Create sample distorted horizontal line (barrel distortion)
    x = np.linspace(0, 100, 50)
    # Perfect straight line
    y_straight = np.full_like(x, 50.0)
    
    # Barrel distortion (quadratic)
    y_barrel = 50 + 0.005 * (x - 50) ** 2
    
    # Wavy distortion (higher order)
    y_wavy = 50 + 2 * np.sin(x * 0.1) + 0.01 * (x - 50) ** 2
    
    fitter = PolynomialFitter(max_order=6)
    
    print("=" * 60)
    print("POLYNOMIAL FITTING DEMO")
    print("=" * 60)
    
    # Test straight line
    points_straight = np.column_stack([x, y_straight])
    analysis_straight = fitter.fit_line(points_straight, line_id=0, line_type="horizontal")
    print(f"\n1. STRAIGHT LINE:")
    print(f"   Best fit order: {analysis_straight.best_fit_order}")
    print(f"   Linear R²: {analysis_straight.fits[0].r_squared:.6f}")
    print(f"   Is perfectly straight: {analysis_straight.is_perfectly_straight}")
    
    # Test barrel distortion
    points_barrel = np.column_stack([x, y_barrel])
    analysis_barrel = fitter.fit_line(points_barrel, line_id=1, line_type="horizontal")
    print(f"\n2. BARREL DISTORTION:")
    print(f"   Recommended order: {analysis_barrel.recommended_order}")
    for fit in analysis_barrel.fits[:4]:
        print(f"   Order {fit.order}: R²={fit.r_squared:.6f}, RMSE={fit.rmse:.4f}, extrema={fit.extrema_type}")
    
    # Test wavy distortion
    points_wavy = np.column_stack([x, y_wavy])
    analysis_wavy = fitter.fit_line(points_wavy, line_id=2, line_type="horizontal")
    print(f"\n3. WAVY DISTORTION:")
    print(f"   Recommended order: {analysis_wavy.recommended_order}")
    for fit in analysis_wavy.fits[:6]:
        print(f"   Order {fit.order}: R²={fit.r_squared:.6f}, extrema={fit.extrema_type}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo_polynomial_fitting()
