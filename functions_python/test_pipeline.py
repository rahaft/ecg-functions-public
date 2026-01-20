"""
Test Pipeline
Simple script to test ECG digitization pipeline with visualization
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt
from digitization_pipeline import ECGDigitizer
from line_visualization import LineVisualizer
from quality_assessment import QualityAssessor


def test_single_image(image_path: str, output_dir: str = 'data/test_output'):
    """
    Test pipeline on a single image
    
    Args:
        image_path: Path to ECG image
        output_dir: Directory to save outputs
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Testing pipeline on: {image_path}")
    print("-" * 50)
    
    # Initialize digitizer with visualization enabled
    digitizer = ECGDigitizer(
        use_segmented_processing=True,
        enable_visualization=True
    )
    
    # Process image
    print("Processing image...")
    result = digitizer.process_image(image_path)
    
    # Get grid info
    grid_info = digitizer.last_grid_info
    
    print(f"\n✓ Processed {len(result['leads'])} leads")
    print(f"  Sampling rate: {result['metadata']['sampling_rate']} Hz")
    
    # Quality assessment
    quality_assessor = QualityAssessor(sampling_rate=digitizer.sampling_rate)
    quality = quality_assessor.assess_quality(result['leads'], grid_info)
    
    print(f"\nQuality Metrics:")
    print(f"  Overall Score: {quality['overall_score']:.3f}")
    print(f"  Mean SNR: {quality['snr']['mean_snr']:.2f} dB")
    if quality['grid_quality']:
        print(f"  Grid Score: {quality['grid_quality']['grid_score']:.3f}")
    print(f"  Clarity Score: {quality['signal_clarity']['clarity_score']:.3f}")
    print(f"  Completeness: {quality['completeness']['overall_completeness']:.3f}")
    
    # Visualize results
    print("\nGenerating visualizations...")
    
    # 1. Grid visualization (already created by digitizer)
    if digitizer.visualizer:
        vis_path = digitizer.visualizer.visualize_grid_lines(
            cv2.imread(image_path, cv2.IMREAD_GRAYSCALE),
            grid_info,
            filename=f"grid_{Path(image_path).stem}"
        )
        print(f"  Grid visualization: {vis_path}")
    
    # 2. Signal plots
    plot_signals(result['leads'], output_dir, Path(image_path).stem)
    
    # 3. Quality report
    save_quality_report(quality, output_dir, Path(image_path).stem)
    
    print(f"\n✓ All outputs saved to: {output_dir}")
    
    return result, quality


def plot_signals(leads: list, output_dir: str, image_name: str):
    """Plot digitized signals"""
    fig, axes = plt.subplots(4, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for i, lead_data in enumerate(leads):
        if i >= 12:
            break
        
        ax = axes[i]
        signal_values = np.array(lead_data['values'])
        time = np.arange(len(signal_values)) / lead_data['sampling_rate']
        
        ax.plot(time, signal_values, linewidth=1.5)
        ax.set_title(f"Lead {lead_data['name']}", fontsize=10)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (mV)')
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(len(leads), 12):
        axes[i].axis('off')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f"{image_name}_signals.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Signal plots: {output_path}")


def save_quality_report(quality: dict, output_dir: str, image_name: str):
    """Save quality report as text"""
    report_path = os.path.join(output_dir, f"{image_name}_quality_report.txt")
    
    with open(report_path, 'w') as f:
        f.write("ECG Digitization Quality Report\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Overall Quality Score: {quality['overall_score']:.3f}\n\n")
        
        f.write("SNR Metrics:\n")
        f.write(f"  Mean SNR: {quality['snr']['mean_snr']:.2f} dB\n")
        f.write(f"  Min SNR: {quality['snr']['min_snr']:.2f} dB\n")
        f.write(f"  Max SNR: {quality['snr']['max_snr']:.2f} dB\n")
        f.write(f"  Std SNR: {quality['snr']['std_snr']:.2f} dB\n\n")
        
        if quality['grid_quality']:
            f.write("Grid Quality:\n")
            f.write(f"  Grid Score: {quality['grid_quality']['grid_score']:.3f}\n")
            f.write(f"  Horizontal Lines: {quality['grid_quality']['num_horizontal_lines']}\n")
            f.write(f"  Vertical Lines: {quality['grid_quality']['num_vertical_lines']}\n")
            f.write(f"  Intersections: {quality['grid_quality']['num_intersections']}\n\n")
        
        f.write("Signal Clarity:\n")
        f.write(f"  Clarity Score: {quality['signal_clarity']['clarity_score']:.3f}\n")
        f.write(f"  Avg Contrast: {quality['signal_clarity']['avg_contrast']:.3f}\n\n")
        
        f.write("Completeness:\n")
        f.write(f"  Completeness Score: {quality['completeness']['overall_completeness']:.3f}\n")
        f.write(f"  Valid Leads: {quality['completeness']['valid_leads']}/{quality['completeness']['num_leads']}\n")
    
    print(f"  Quality report: {report_path}")


def interactive_test():
    """Interactive test mode"""
    print("ECG Digitization Pipeline - Interactive Test")
    print("=" * 50)
    
    # Get image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter path to ECG image: ").strip().strip('"')
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    # Test the image
    try:
        result, quality = test_single_image(image_path)
        print("\n✓ Test completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    interactive_test()
