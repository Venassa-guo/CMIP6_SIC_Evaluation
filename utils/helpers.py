import numpy as np
import pandas as pd
import cftime
from pyproj import Proj

# ===================== Projection Parameters (NSIDC PSN25) =====================
# 100km resolution PSN projection parameters (matches combined_sic_psn25.100km.nc)
PSN100_PROJ = Proj({
    'proj': 'stere', 'lat_0': 90, 'lat_ts': 70, 'lon_0': -45, 
    'k': 1, 'x_0': 0, 'y_0': 0, 'datum': 'WGS84', 'units': 'm', 'no_defs': True
})
WGS84_PROJ = Proj(proj='latlong', datum='WGS84')

# ===================== Temporal Processing Utilities =====================
def fix_time_bound_for_calendar(time_da, start_str, end_str):
    """Adapt to cftime types (DatetimeNoLeap/360Day) and correct illegal date boundaries."""
    # 1. Manually correct illegal dates (e.g., Dec 31st doesn't exist in 360-day calendar)
    end_str_fixed = end_str.replace('12-31', '12-30')  
    start_str_fixed = start_str.replace('02-29', '02-28')  
    
    # 2. Split date strings
    def split_date_str(date_str):
        parts = date_str.split('-')
        return int(parts[0]), int(parts[1]), int(parts[2])
    
    start_year, start_month, start_day = split_date_str(start_str_fixed)
    end_year, end_month, end_day = split_date_str(end_str_fixed)
    
    # 3. Iterate through the time axis to match indices
    time_vals = time_da.values
    start_idx, end_idx = None, None
    for i, t in enumerate(time_vals):
        if t.year == start_year and t.month == start_month and t.day == start_day:
            start_idx = i
        if t.year == end_year and t.month == end_month and t.day == end_day:
            end_idx = i + 1 
            
    # 4. Boundary fallback handling
    if start_idx is None: start_idx = 0
    if end_idx is None: end_idx = len(time_vals)
        
    return time_vals[start_idx], time_vals[end_idx-1] if end_idx > 0 else time_vals[-1]

def cftime_to_datetime_safe(cftime_vals):
    """Convert cftime arrays to pandas-compatible datetime arrays with ultimate fallback."""
    try:
        if isinstance(cftime_vals.values[0], (cftime.DatetimeNoLeap, cftime.Datetime360Day, cftime.DatetimeAllLeap)):
            time_str = []
            for t in cftime_vals.values:
                try:
                    time_str.append(f"{t.year}-{t.month:02d}-{t.day:02d}")
                except:
                    time_str.append(f"{t.year}-01-01")
            return pd.to_datetime(time_str)
        else:
            return pd.to_datetime(cftime_vals.values)
    except Exception:
        # Ultimate fallback: generate standard sequential time if parsing completely fails
        print("⚠️ Triggered ultimate fallback: generating sequential time range.")
        return pd.date_range(start='1980-01-01', periods=len(cftime_vals), freq='MS')

# ===================== Spatial Processing Utilities =====================
def get_spatial_mask(da_lat, da_lon, lat_min, lat_max, lon_min, lon_max):
    """Create lat/lon mask (handles time dimension + converts 0-360 longitude to -180-180)."""
    if 'time' in da_lat.dims: da_lat = da_lat.isel(time=0)
    if 'time' in da_lon.dims: da_lon = da_lon.isel(time=0)
        
    # Longitude format conversion
    if da_lon.max() > 180:
        da_lon = (da_lon + 180) % 360 - 180
        
    mask = (da_lat >= lat_min) & (da_lat <= lat_max) & (da_lon >= lon_min) & (da_lon <= lon_max)
    if not mask.any():
        print(f"⚠️ Warning: No valid data within {lat_min}-{lat_max}N, {lon_min}-{lon_max}W")
    return mask
