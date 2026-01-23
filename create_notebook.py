import json

# Read all cell files
with open('kaggle_cell_1_grid_detection.py', 'r', encoding='utf-8') as f:
    cell1 = f.read().splitlines(True)

with open('kaggle_cell_2_segmented_processing.py', 'r', encoding='utf-8') as f:
    cell2 = f.read().splitlines(True)

with open('kaggle_cell_3_line_visualization.py', 'r', encoding='utf-8') as f:
    cell3 = f.read().splitlines(True)

with open('KAGGLE_CELL_4_READY_TO_PASTE.py', 'r', encoding='utf-8') as f:
    cell4 = f.read().splitlines(True)

with open('kaggle_cell_5_complete.py', 'r', encoding='utf-8') as f:
    cell5 = f.read().splitlines(True)

with open('kaggle_cell_6_verify.py', 'r', encoding='utf-8') as f:
    cell6 = f.read().splitlines(True)

# Create notebook structure
notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# ECG Image Digitization - Complete Kaggle Notebook\n",
                "\n",
                "**IMPORTANT:** Make sure to attach the competition dataset before running!\n",
                "\n",
                "This notebook includes Feature 1 improvements:\n",
                "- Enhanced Grid Detection & Validation\n",
                "- Adaptive Line Detection Thresholds\n",
                "- Improved Grid Spacing Calculation"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell1
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell2
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell3
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell4
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell5
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": cell6
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.7.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

# Write notebook
with open('kaggle_complete_notebook.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("✅ Notebook created: kaggle_complete_notebook.ipynb")
print("   Contains 6 cells with Feature 1 improvements")
