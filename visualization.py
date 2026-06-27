import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import os

# ===================== Academic Plotting Global Configurations =====================
plt.rcParams["font.family"] = "Arial" # Standard academic font
plt.rcParams["axes.unicode_minus"] = False 
plt.rcParams["axes.linewidth"] = 1.0
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.direction"] = "in"
plt.rcParams["xtick.top"] = True
plt.rcParams["ytick.right"] = True

# Polar stereographic projection (matches PSN100 in helpers)
PROJ = ccrs.Stereographic(central_latitude=90, central_longitude=-45, true_scale_latitude=70)

def plot_sic_comparison(cesm2_data, hadgem3_data, save_path):
    """Plot CESM2 + HadGEM3 polar comparison map (2x3 multi-panel)."""
    fig = plt.figure(figsize=(18, 14), facecolor='white')
    
    # Global English title
    main_title = 'September Sea Ice Concentration in Greenland (1980-2009) - Model Comparison'
    fig.text(x=0.5, y=0.98, s=main_title, fontsize=20, fontweight='bold', ha='center')
    
    # Dynamically add subplots (Top row: CESM2, Bottom row: HadGEM3)
    axes_positions = [
        [0.05, 0.52, 0.28, 0.35], [0.36, 0.52, 0.28, 0.35], [0.67, 0.52, 0.28, 0.35],
        [0.05, 0.12, 0.28, 0.35], [0.36, 0.12, 0.28, 0.35], [0.67, 0.12, 0.28, 0.35]
    ]
    
    all_axes = [fig.add_axes(pos, projection=PROJ) for pos in axes_positions]
    
    for i, ax in enumerate(all_axes):
        ax.coastlines(resolution='50m', color='black', linewidth=1, zorder=2)
        ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=1)
        ax.set_title(f"Decade {i+1}", fontsize=14)
        
    # Colorbar configuration (percentage display)
    cbar_ax = fig.add_axes([0.15, 0.05, 0.7, 0.02])
    # Create a mock ScalarMappable for the colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=0.15, vmax=1.0))
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_ticks(np.arange(0.15, 1.01, 0.1))
    cbar.set_ticklabels([f'{int(x*100)}%' for x in np.arange(0.15, 1.01, 0.1)])
    cbar.ax.tick_params(labelsize=14)
    cbar.outline.set_linewidth(1)
    cbar.outline.set_color('gray')
    
    # Save figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, facecolor='white', bbox_inches='tight', pad_inches=0.1)
    plt.close()
    print(f"✅ Comparison plot saved to: {save_path}")

def plot_sic_timeseries(obs_time, obs_vals, model_time, model_vals, save_path):
    """Plot time series line chart."""
    plt.figure(figsize=(12, 6))
    
    plt.plot(obs_time, obs_vals, label='NSIDC Obs (Greenland)', 
             linewidth=2, color='#F18F01', linestyle='--')
    if model_time is not None:
        plt.plot(model_time, model_vals, label='CMIP6 Model', 
                 linewidth=2, color='#1F77B4', linestyle='-')
                 
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Sea Ice Concentration', fontsize=14)
    plt.legend(fontsize=12, loc='best')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.savefig(save_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"✅ Time series plot saved to: {save_path}")
