import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path

base_dir = Path(__file__).parent
brain_dir = Path(r'C:\Users\kwzj4\.gemini\antigravity-ide\brain\d0df90a7-e139-44d3-9b80-263c7fa34a7b')
r1_csv = base_dir / 'reports' / 'r1_validation_results.csv'
r2_csv = base_dir / 'reports' / 'r2_ablation_results.csv'
par_csv = base_dir / 'reports' / 'pareto_frontier_summary.csv'

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# 1. R1 Figure
if r1_csv.exists():
    df_r1 = pd.read_csv(r1_csv)
    summary_r1 = df_r1.groupby('policy')[['utility', 'gini', 'p10', 'completed_trips']].agg(['mean', 'std'])
    order = ['MOMAQL', 'Greedy', 'Nearest', 'LAF', 'Exact REASSIGN']
    labels = ['MOMAQL (2D)', 'Greedy', 'Nearest', 'LAF', 'REASSIGN']
    colors = ['#2563eb', '#dc2626', '#d97706', '#16a34a', '#9333ea']
    
    means_u = [summary_r1.loc[p, ('utility', 'mean')] / 1e6 for p in order]
    stds_u = [summary_r1.loc[p, ('utility', 'std')] / 1e6 for p in order]
    means_g = [summary_r1.loc[p, ('gini', 'mean')] for p in order]
    stds_g = [summary_r1.loc[p, ('gini', 'std')] for p in order]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    bars1 = ax1.bar(labels, means_u, yerr=stds_u, color=colors, capsize=4, width=0.55, edgecolor='#0f172a', alpha=0.9)
    ax1.set_title('R1: Total Net Utility Comparison', fontsize=12, fontweight='bold', pad=12)
    ax1.set_ylabel('Total Utility (Million USD)', fontsize=11)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    for bar, val in zip(bars1, means_u):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03, f'{val:.3f}M', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    bars2 = ax2.bar(labels, means_g, yerr=stds_g, color=colors, capsize=4, width=0.55, edgecolor='#0f172a', alpha=0.9)
    ax2.set_title('R1: Income Inequality (Gini Index)', fontsize=12, fontweight='bold', pad=12)
    ax2.set_ylabel('Gini Coefficient (Lower = More Fair)', fontsize=11)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    for bar, val in zip(bars2, means_g):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    fig.savefig(brain_dir / 'r1_validation_unified_comparison.png')
    plt.close()

# 2. R2 Ablation Figure
if r2_csv.exists():
    df_r2 = pd.read_csv(r2_csv)
    order_r2 = ['full', 'no_forecast', 'no_fairness']
    labels_r2 = ['Full MOMAQL (2D)', 'No Forecast (Q=0)', 'No Fairness (lambda=0)']
    colors_r2 = ['#2563eb', '#64748b', '#e11d48']
    
    means_u = [df_r2.loc[df_r2['ablation']==a, 'utility_mean'].values[0] / 1e6 for a in order_r2]
    stds_u = [df_r2.loc[df_r2['ablation']==a, 'utility_std'].values[0] / 1e6 for a in order_r2]
    means_g = [df_r2.loc[df_r2['ablation']==a, 'gini_mean'].values[0] for a in order_r2]
    stds_g = [df_r2.loc[df_r2['ablation']==a, 'gini_std'].values[0] for a in order_r2]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    bars1 = ax1.bar(labels_r2, means_u, yerr=stds_u, color=colors_r2, capsize=4, width=0.5, edgecolor='#0f172a', alpha=0.9)
    ax1.set_title('R2 Ablation: Net Utility (Million USD)', fontsize=12, fontweight='bold', pad=12)
    ax1.set_ylabel('Total Utility (Million USD)', fontsize=11)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)
    for bar, val in zip(bars1, means_u):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03, f'{val:.3f}M', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    bars2 = ax2.bar(labels_r2, means_g, yerr=stds_g, color=colors_r2, capsize=4, width=0.5, edgecolor='#0f172a', alpha=0.9)
    ax2.set_title('R2 Ablation: Gini Coefficient', fontsize=12, fontweight='bold', pad=12)
    ax2.set_ylabel('Gini Index', fontsize=11)
    ax2.grid(axis='y', linestyle='--', alpha=0.5)
    for bar, val in zip(bars2, means_g):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.4f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    fig.savefig(brain_dir / 'r2_ablation_unified_comparison.png')
    plt.close()

# 3. Pareto Figure
if par_csv.exists():
    df_par = pd.read_csv(par_csv)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    
    lams = df_par['lambda']
    u_vals = df_par['utility_mean'] / 1e6
    g_vals = df_par['gini_mean']
    
    ax1.plot(lams, u_vals, marker='o', color='#2563eb', linewidth=2.2, label='Utility')
    ax1.set_xlabel('Fairness Weight (lambda)', fontsize=11)
    ax1.set_ylabel('Total Utility (Million USD)', color='#2563eb', fontsize=11)
    ax1.tick_params(axis='y', labelcolor='#2563eb')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot(lams, g_vals, marker='s', color='#dc2626', linewidth=2.2, linestyle='--', label='Gini Index')
    ax1_twin.set_ylabel('Gini Index (Lower = Fairer)', color='#dc2626', fontsize=11)
    ax1_twin.tick_params(axis='y', labelcolor='#dc2626')
    ax1.set_title('Pareto Frontier: Lambda Trade-off Curve', fontsize=12, fontweight='bold', pad=12)
    
    ax2.plot(g_vals, u_vals, marker='o', color='#7c3aed', linewidth=2.2)
    for i, row in df_par.iterrows():
        l_val = row['lambda']
        ax2.annotate(f'lambda={l_val:.1f}', (row['gini_mean'], row['utility_mean']/1e6), textcoords='offset points', xytext=(6, 4), fontsize=8.5, fontweight='bold')
    ax2.set_xlabel('Gini Index (Inequality)', fontsize=11)
    ax2.set_ylabel('Total Utility (Million USD)', fontsize=11)
    ax2.set_title('Objective Space: Efficiency vs Fairness', fontsize=12, fontweight='bold', pad=12)
    ax2.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    fig.savefig(brain_dir / 'pareto_frontier_unified_curve.png')
    plt.close()

print('ALL_FIGURES_GENERATED_SUCCESSFULLY')
