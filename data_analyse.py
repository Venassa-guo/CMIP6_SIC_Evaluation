import xarray as xr
import numpy as np
import os
from utils.helpers import fix_time_bound_for_calendar, get_spatial_mask, cftime_to_datetime_safe

# ===================== Global Configurations & Paths =====================
# Greenland Fjord boundaries
TARGET_LAT_MIN, TARGET_LAT_MAX = 60, 75
TARGET_LON_MIN, TARGET_LON_MAX = -50, -10

# It is recommended to use relative paths. Place your NetCDF files in the './data' folder.
BASE_DIR = "./data" 
cesm2_path = os.path.join(BASE_DIR, "siconc_CESM2_1980-2014.nc")
hadgem3_path = os.path.join(BASE_DIR, "HadGEM3_MM_hist.nc")
obs_path = os.path.join(BASE_DIR, "combined_sic_psn25.100km.nc")

# Future scenario paths (SSP2-4.5)
hadgem3_future_path1 = os.path.join(BASE_DIR, "siconc_SImon_HadGEM3-GC31-LL_ssp245_r1i1p1f3_gn_201501-204912.nc")
hadgem3_future_path2 = os.path.join(BASE_DIR, "siconc_SImon_HadGEM3-GC31-LL_ssp245_r1i1p1f3_gn_205001-210012.nc")

# ===================== Core Processing Functions =====================
def get_sic_var(ds):
    """Automatically identify the Sea Ice Concentration variable name."""
    var_list = list(ds.data_vars.keys())
    if 'siconc' in var_list: return 'siconc'
    if 'cdr_seaice_conc_monthly' in var_list: return 'cdr_seaice_conc_monthly'
    raise ValueError(f"SIC variable not found in dataset. Available variables: {var_list}")

def safe_time_slice(ds, start, end):
    """Safely clip the time dimension and print validation info."""
    try:
        start_t, end_t = fix_time_bound_for_calendar(ds.time, start, end)
        ds_slice = ds.sel(time=slice(start_t, end_t))
        print(f"Clipped time range: {ds_slice['time'].min().values} -> {ds_slice['time'].max().values}")
        return ds_slice
    except Exception as e:
        print(f"⚠️ Time clipping failed: {e}")
        return ds

def crop_and_average_sic(sic_da, lat_da, lon_da):
    """Crop the target region and calculate the spatial average."""
    mask = get_spatial_mask(lat_da, lon_da, TARGET_LAT_MIN, TARGET_LAT_MAX, TARGET_LON_MIN, TARGET_LON_MAX)
    if 'time' in sic_da.dims and 'time' not in mask.dims:
        mask = mask.expand_dims(time=sic_da.time)
    sic_crop = sic_da.where(mask, drop=True)
    spatial_dims = [dim for dim in ['nj', 'ni', 'lat', 'lon', 'y', 'x'] if dim in sic_crop.dims]
    return sic_crop.mean(dim=spatial_dims)

def crop_hadgem3_future(file_path):
    """Dask-free cropping function for future HadGEM3 scenarios (adapts to 2D grids)."""
    ds = xr.open_dataset(file_path)
    var_name = get_sic_var(ds)
    # Simplified spatial cropping logic
    mask = get_spatial_mask(ds.lat, ds.lon, 59, 83, -74, -10)
    ds_clipped = ds.where(mask, drop=True)
    return ds_clipped

# ===================== Main Execution Flow =====================
if __name__ == "__main__":
    print("✅ Starting CMIP6 SIC data processing pipeline...")
    
    # 1. Load historical data and validate
    try:
        obs_data = xr.open_dataset(obs_path)
        obs_var = get_sic_var(obs_data)
        obs_sic_mean = crop_and_average_sic(obs_data[obs_var], obs_data.lat, obs_data.lon)
        obs_sic_mean = safe_time_slice(obs_sic_mean, '1980-01-01', '2014-12-31')
        print(f"📊 Observation data length: {len(obs_sic_mean)}")
    except FileNotFoundError:
        print(f"❌ Observation data file not found: {obs_path}")

    # 2. Validate future scenario cropped grid count
    if os.path.exists(hadgem3_future_path1):
        ds_check = crop_hadgem3_future(hadgem3_future_path1)
        spatial_dims = [d for d in ds_check.dims if d not in ["time"]]
        total_grid = np.prod([ds_check[d].size for d in spatial_dims])
        print(f"📊 Clipped HadGEM3 future data dimensions: {ds_check.dims}")
        print(f"📊 Valid grid cells in Greenland Fjords: {total_grid}")
        
    print("✅ Data processing pipeline execution completed!")
