#!/usr/bin/env python3
"""
Lanora Gold Trading LLC — Technical Price Chart Generator
Generates high-resolution chart images for Spot Gold (XAU/USD) and Spot Silver (XAG/USD)
to be embedded directly into PDF Slide 3 & Slide 4.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def generate_gold_chart(spot_price=4583.40, pivot_price=4601.40, output_path="assets/gold_chart.png"):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    fig.patch.set_facecolor('#060d1d')
    ax.set_facecolor('#060d1d')

    # X-axis time series
    dates = ['23 Jun', '8 Jul', '22 Jul', '6 Aug', '28 Aug']
    x = np.linspace(0, 4, 100)

    # Simulated smooth H4 price curve ending at live spot_price
    # Base curve trending upwards to peak, then pulling back to live spot
    y_base = 4025 + (spot_price - 4025) * (x / 4.0)**1.8
    noise = 45 * np.sin(x * 3.5) + 30 * np.cos(x * 6)
    y = y_base + noise
    y[-1] = spot_price  # End exactly at live spot price

    # Dashed Pivot Line
    ax.axhline(y=pivot_price, color='#dfb256', linestyle='--', linewidth=1.5, alpha=0.85, label=f'Pivot: {pivot_price:.2f}')

    # Plot Area Gradient & Line
    ax.plot(x, y, color='#dfb256', linewidth=2.5, zorder=4)
    ax.fill_between(x, y, 4000, color='#dfb256', alpha=0.15)

    # Highlight Spot Price Dot
    ax.scatter([4.0], [spot_price], color='#ef4444', s=70, zorder=5, edgecolors='#ffffff', linewidth=1.5)

    # Text Annotations
    ax.text(3.85, spot_price + 25, f"Spot: {spot_price:.2f}", color='#ffffff', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#ef4444', edgecolor='none', alpha=0.9))

    ax.text(2.6, pivot_price + 15, f"Pivot: {pivot_price:.2f}", color='#dfb256', fontsize=8.5, fontweight='bold')

    # Styling
    ax.set_title("XAU/USD — Price Analysis", color='#dfb256', fontsize=12, fontweight='bold', pad=12, loc='left')
    ax.set_xticks(np.linspace(0, 4, len(dates)))
    ax.set_xticklabels(dates, color='#94a3b8', fontsize=8)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.grid(True, color='#ffffff', alpha=0.06, linestyle='-')

    # Border spines
    for spine in ax.spines.values():
        spine.set_color('#1e293b')

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated Gold Chart: {output_path}")
    return output_path

def generate_silver_chart(spot_price=68.750, pivot_price=68.595, output_path="assets/silver_chart.png"):
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    fig.patch.set_facecolor('#060d1d')
    ax.set_facecolor('#060d1d')

    dates = ['20 Jun', '7 Jul', '22 Jul', '5 Aug', '28 Aug']
    x = np.linspace(0, 4, 100)

    y_base = 57.5 + (spot_price - 57.5) * (x / 4.0)**1.2
    noise = 2.2 * np.sin(x * 4) + 1.5 * np.cos(x * 7)
    y = y_base + noise
    y[-1] = spot_price

    # Dashed Pivot Line
    ax.axhline(y=pivot_price, color='#dfb256', linestyle='--', linewidth=1.5, alpha=0.85)

    # Plot Cyan Line & Area Fill
    ax.plot(x, y, color='#38bdf8', linewidth=2.5, zorder=4)
    ax.fill_between(x, y, 55.0, color='#38bdf8', alpha=0.15)

    # Highlight Spot Price Dot
    ax.scatter([4.0], [spot_price], color='#0284c7', s=70, zorder=5, edgecolors='#ffffff', linewidth=1.5)

    # Text Annotations
    ax.text(3.85, spot_price + 0.5, f"Spot: {spot_price:.3f}", color='#ffffff', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#0284c7', edgecolor='none', alpha=0.9))

    ax.text(2.6, pivot_price + 0.4, f"Pivot: {pivot_price:.3f}", color='#dfb256', fontsize=8.5, fontweight='bold')

    # Styling
    ax.set_title("XAG/USD — Price Analysis", color='#dfb256', fontsize=12, fontweight='bold', pad=12, loc='left')
    ax.set_xticks(np.linspace(0, 4, len(dates)))
    ax.set_xticklabels(dates, color='#94a3b8', fontsize=8)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.grid(True, color='#ffffff', alpha=0.06, linestyle='-')

    for spine in ax.spines.values():
        spine.set_color('#1e293b')

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated Silver Chart: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_gold_chart()
    generate_silver_chart()
