"""
Fit Analyzer - Analyzes grid lines and recommends transformations

This module integrates with the polynomial fitter to provide
a comprehensive analysis of grid line distortion and recommend
the best transformation approach.

Output Format (for UI menu):
{
    "fits": [
        {
            "name": "Linear (y=mx+b)",
            "order": 1,
            "horizontal_r2": 0.95,
            "vertical_r2": 0.94,
            "combined_r2": 0.945,
            "avg_deviation": 2.3,
            "deviation_histogram": {...},
            "extrema": "none",
            "recommended": false
        },
        {
            "name": "Quadratic (Barrel)",
            "order": 2,
            "horizontal_r2": 0.999,
            "vertical_r2": 0.998,
            "combined_r2": 0.9985,
            "avg_deviation": 0.1,
            "deviation_histogram": {...},
            "extrema": "single",
            "recommended": true
        },
        ...
    ],
    "best_fit": {...},
    "summary": {...}
}
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .polynomial_fitter import PolynomialFitter, LineFitAnalysis, FitResult


@dataclass
class FitOption:
    """A single fit option for the UI menu"""
    name: str
    order: int
    formula: str
    horizontal_r2: float
    vertical_r2: float
    combined_r2: float
    avg_deviation_px: float
    max_deviation_px: float
    points_perfect: int  # Points with 0 deviation
    points_under_half_px: int  # Points with <0.5px deviation
    points_under_1px: int  # Points with <1px deviation
    total_points: int
    extrema_type: str  # "none", "single", "multiple"
    num_extrema: int
    is_monotonic: bool
    recommended: bool
    category: str  # "straight", "simple_curve", "complex_curve", "wiggly"
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "order": self.order,
            "formula": self.formula,
            "horizontal_r2": round(self.horizontal_r2, 6),
            "vertical_r2": round(self.vertical_r2, 6),
            "combined_r2": round(self.combined_r2, 6),
            "avg_deviation_px": round(self.avg_deviation_px, 4),
            "max_deviation_px": round(self.max_deviation_px, 4),
            "accuracy_stats": {
                "perfect_fit_points": self.points_perfect,
                "under_half_px": self.points_under_half_px,
                "under_1px": self.points_under_1px,
                "total_points": self.total_points,
                "percent_perfect": round(100 * self.points_perfect / max(self.total_points, 1), 1),
                "percent_under_half_px": round(100 * self.points_under_half_px / max(self.total_points, 1), 1),
                "percent_under_1px": round(100 * self.points_under_1px / max(self.total_points, 1), 1)
            },
            "extrema_type": self.extrema_type,
            "num_extrema": self.num_extrema,
            "is_monotonic": self.is_monotonic,
            "recommended": self.recommended,
            "category": self.category
        }


class FitAnalyzer:
    """
    Analyzes detected grid lines and provides fit options for UI display.
    """
    
    # Polynomial order names and formulas
    ORDER_INFO = {
        1: ("Linear", "y = mx + b"),
        2: ("Quadratic (Barrel)", "y = ax² + bx + c"),
        3: ("Cubic", "y = ax³ + bx² + cx + d"),
        4: ("Quartic", "y = ax⁴ + bx³ + cx² + dx + e"),
        5: ("Quintic", "y = ax⁵ + ..."),
        6: ("6th Order", "y = ax⁶ + ..."),
        7: ("7th Order", "y = ax⁷ + ..."),
        8: ("8th Order", "y = ax⁸ + ..."),
    }
    
    def __init__(self, max_order: int = 6):
        self.max_order = max_order
        self.fitter = PolynomialFitter(max_order=max_order)
        
    def analyze_grid(self, horizontal_lines: List[np.ndarray],
                     vertical_lines: List[np.ndarray]) -> Dict:
        """
        Analyze all grid lines and generate fit options menu.
        
        Args:
            horizontal_lines: List of Nx2 arrays for horizontal line points
            vertical_lines: List of Nx2 arrays for vertical line points
            
        Returns:
            Dictionary with fit options and recommendations
        """
        # Analyze each line
        h_analyses = []
        v_analyses = []
        
        for i, points in enumerate(horizontal_lines):
            if len(points) >= 3:
                analysis = self.fitter.fit_line(points, line_id=i, line_type="horizontal")
                h_analyses.append(analysis)
        
        for i, points in enumerate(vertical_lines):
            if len(points) >= 3:
                analysis = self.fitter.fit_line(points, line_id=i, line_type="vertical")
                v_analyses.append(analysis)
        
        if not h_analyses and not v_analyses:
            return {
                "error": "No valid lines detected",
                "fits": [],
                "best_fit": None
            }
        
        # Generate fit options for each polynomial order
        fit_options = []
        best_combined_r2 = -1
        best_order = 1
        
        for order in range(1, self.max_order + 1):
            option = self._create_fit_option(order, h_analyses, v_analyses)
            if option:
                fit_options.append(option)
                if option.combined_r2 > best_combined_r2:
                    best_combined_r2 = option.combined_r2
                    best_order = order
        
        # Mark the recommended option
        for option in fit_options:
            option.recommended = (option.order == best_order)
        
        # Categorize fits
        self._categorize_fits(fit_options)
        
        # Generate summary
        summary = self._generate_summary(fit_options, h_analyses, v_analyses, best_order)
        
        return {
            "fits": [opt.to_dict() for opt in fit_options],
            "best_fit": fit_options[best_order - 1].to_dict() if best_order <= len(fit_options) else None,
            "summary": summary,
            "line_counts": {
                "horizontal": len(h_analyses),
                "vertical": len(v_analyses)
            }
        }
    
    def _create_fit_option(self, order: int, 
                           h_analyses: List[LineFitAnalysis],
                           v_analyses: List[LineFitAnalysis]) -> Optional[FitOption]:
        """Create a FitOption for a specific polynomial order."""
        
        h_r2_values = []
        v_r2_values = []
        all_deviations = []
        max_devs = []
        histogram_totals = {"perfect (0)": 0, "<0.5px": 0, "0.5-1px": 0, "1-2px": 0, ">2px": 0}
        extrema_types = []
        num_extrema_list = []
        monotonic_count = 0
        total_points = 0
        
        # Collect horizontal line stats
        for analysis in h_analyses:
            for fit in analysis.fits:
                if fit.order == order:
                    h_r2_values.append(fit.r_squared)
                    all_deviations.append(fit.mae)
                    max_devs.append(fit.max_deviation)
                    for key, val in fit.deviation_histogram.items():
                        if key in histogram_totals:
                            histogram_totals[key] += val
                    extrema_types.append(fit.extrema_type)
                    num_extrema_list.append(fit.num_extrema)
                    if fit.is_monotonic:
                        monotonic_count += 1
                    total_points += len(fit.residuals)
                    break
        
        # Collect vertical line stats
        for analysis in v_analyses:
            for fit in analysis.fits:
                if fit.order == order:
                    v_r2_values.append(fit.r_squared)
                    all_deviations.append(fit.mae)
                    max_devs.append(fit.max_deviation)
                    for key, val in fit.deviation_histogram.items():
                        if key in histogram_totals:
                            histogram_totals[key] += val
                    extrema_types.append(fit.extrema_type)
                    num_extrema_list.append(fit.num_extrema)
                    if fit.is_monotonic:
                        monotonic_count += 1
                    total_points += len(fit.residuals)
                    break
        
        if not h_r2_values and not v_r2_values:
            return None
        
        # Calculate averages
        h_r2 = np.mean(h_r2_values) if h_r2_values else 0
        v_r2 = np.mean(v_r2_values) if v_r2_values else 0
        combined_r2 = np.mean(h_r2_values + v_r2_values)
        avg_dev = np.mean(all_deviations) if all_deviations else 0
        max_dev = np.max(max_devs) if max_devs else 0
        
        # Determine predominant extrema type
        if extrema_types:
            if extrema_types.count("multiple") > len(extrema_types) / 3:
                extrema_type = "multiple"
            elif extrema_types.count("single") > len(extrema_types) / 3:
                extrema_type = "single"
            else:
                extrema_type = "none"
        else:
            extrema_type = "none"
        
        avg_extrema = int(np.mean(num_extrema_list)) if num_extrema_list else 0
        is_monotonic = monotonic_count > len(extrema_types) / 2 if extrema_types else True
        
        name, formula = self.ORDER_INFO.get(order, (f"Order {order}", f"y = polynomial({order})"))
        
        return FitOption(
            name=name,
            order=order,
            formula=formula,
            horizontal_r2=h_r2,
            vertical_r2=v_r2,
            combined_r2=combined_r2,
            avg_deviation_px=avg_dev,
            max_deviation_px=max_dev,
            points_perfect=histogram_totals.get("perfect (0)", 0),
            points_under_half_px=histogram_totals.get("perfect (0)", 0) + histogram_totals.get("<0.5px", 0),
            points_under_1px=histogram_totals.get("perfect (0)", 0) + histogram_totals.get("<0.5px", 0) + histogram_totals.get("0.5-1px", 0),
            total_points=total_points,
            extrema_type=extrema_type,
            num_extrema=avg_extrema,
            is_monotonic=is_monotonic,
            recommended=False,  # Set later
            category=""  # Set later
        )
    
    def _categorize_fits(self, fit_options: List[FitOption]):
        """Categorize each fit option based on its characteristics."""
        
        for opt in fit_options:
            if opt.order == 1:
                if opt.combined_r2 >= 0.999:
                    opt.category = "straight"
                else:
                    opt.category = "needs_correction"
            elif opt.extrema_type == "none":
                opt.category = "straight"
            elif opt.extrema_type == "single":
                opt.category = "simple_curve"  # Barrel/pincushion
            else:  # multiple
                opt.category = "wiggly"
    
    def _generate_summary(self, fit_options: List[FitOption],
                          h_analyses: List[LineFitAnalysis],
                          v_analyses: List[LineFitAnalysis],
                          best_order: int) -> Dict:
        """Generate a summary of the analysis."""
        
        # Check if linear fit is perfect
        linear_perfect = False
        if fit_options and fit_options[0].combined_r2 >= 0.9999:
            linear_perfect = True
        
        # Find best option
        best_option = None
        for opt in fit_options:
            if opt.order == best_order:
                best_option = opt
                break
        
        # Determine transformation recommendation
        if linear_perfect:
            recommendation = "No transformation needed - lines are perfectly straight"
            transform_type = "none"
        elif best_order == 2:
            recommendation = "Apply Barrel/Pincushion correction (quadratic)"
            transform_type = "barrel"
        elif best_order == 3:
            recommendation = "Apply Cubic correction"
            transform_type = "cubic"
        elif best_order >= 4:
            if best_option and best_option.extrema_type == "multiple":
                recommendation = f"Apply Wiggly correction (order {best_order}) - multiple curves detected"
                transform_type = "wiggly"
            else:
                recommendation = f"Apply High-order polynomial correction (order {best_order})"
                transform_type = f"polynomial_{best_order}"
        else:
            recommendation = "Linear correction may be sufficient"
            transform_type = "linear"
        
        return {
            "lines_analyzed": {
                "horizontal": len(h_analyses),
                "vertical": len(v_analyses),
                "total": len(h_analyses) + len(v_analyses)
            },
            "linear_fit_perfect": linear_perfect,
            "best_order": best_order,
            "best_r_squared": best_option.combined_r2 if best_option else 0,
            "recommendation": recommendation,
            "transform_type": transform_type,
            "categories_found": list(set(opt.category for opt in fit_options if opt.category))
        }


def demo_fit_analyzer():
    """Demonstrate the fit analyzer."""
    
    # Create sample distorted grid
    np.random.seed(42)
    
    # Barrel-distorted horizontal lines
    h_lines = []
    for y_base in [20, 40, 60, 80]:
        x = np.linspace(0, 100, 30)
        y = y_base + 0.003 * (x - 50) ** 2 + np.random.normal(0, 0.1, len(x))
        h_lines.append(np.column_stack([x, y]))
    
    # Barrel-distorted vertical lines
    v_lines = []
    for x_base in [20, 40, 60, 80]:
        y = np.linspace(0, 100, 30)
        x = x_base + 0.003 * (y - 50) ** 2 + np.random.normal(0, 0.1, len(y))
        v_lines.append(np.column_stack([x, y]))
    
    analyzer = FitAnalyzer(max_order=6)
    result = analyzer.analyze_grid(h_lines, v_lines)
    
    print("=" * 70)
    print("FIT ANALYZER DEMO - Menu Options")
    print("=" * 70)
    
    print("\n📊 FIT OPTIONS MENU:")
    print("-" * 70)
    for fit in result["fits"]:
        rec = "⭐ RECOMMENDED" if fit["recommended"] else ""
        print(f"\n{fit['order']}. {fit['name']} ({fit['formula']})")
        print(f"   Combined R²: {fit['combined_r2']:.6f}  |  Avg Deviation: {fit['avg_deviation_px']:.3f}px")
        print(f"   Horizontal R²: {fit['horizontal_r2']:.6f}  |  Vertical R²: {fit['vertical_r2']:.6f}")
        print(f"   Perfect fit points: {fit['accuracy_stats']['percent_perfect']:.1f}%")
        print(f"   Category: {fit['category']}  |  Extrema: {fit['extrema_type']}")
        if rec:
            print(f"   {rec}")
    
    print("\n" + "-" * 70)
    print("📋 SUMMARY:")
    summary = result["summary"]
    print(f"   Lines analyzed: {summary['lines_analyzed']['total']}")
    print(f"   Best polynomial order: {summary['best_order']}")
    print(f"   Best R²: {summary['best_r_squared']:.6f}")
    print(f"   Recommendation: {summary['recommendation']}")
    print("=" * 70)


if __name__ == "__main__":
    demo_fit_analyzer()
