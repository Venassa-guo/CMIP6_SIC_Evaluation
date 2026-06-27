import xarray as xr
import numpy as np
from scipy.interpolate import griddata

def process_single_decade_wind_data(ds):
    """
    Process single-decade wind field data: 
    dynamically identify coordinates, convert longitudes, and mitigate circular artifacts.
    """
    # 1. Dynamically identify coordinate keys (prevents KeyError)
    lon_key = 'lon' if 'lon' in ds.coords else 'longitude'
    lat_key = 'lat' if 'lat' in ds.coords else 'latitude'
    
    lon = ds[lon_key].values
    lat = ds[lat_key].values
    
    # 2. Convert longitude from 0-360 to -180-180
    if np.max(lon) > 180:
        lon = (lon + 180) % 360 - 180
        # Sort and concatenate data along the longitude dimension to fix artifacts
        sort_idx = np.argsort(lon)
        lon = lon[sort_idx]
        ds = ds.isel({lon_key: sort_idx})
        
    # 3. Check and build Meshgrid (adapts to 1D/2D arrays)
    if lon.ndim == 1 and lat.ndim == 1:
        lon_grid, lat_grid = np.meshgrid(lon, lat)
    else:
        lon_grid, lat_grid = lon, lat
        
    # 4. Target high-resolution grid (for interpolation)
    target_lon = np.arange(np.min(lon_grid), np.max(lon_grid), 0.1)
    target_lat = np.arange(np.min(lat_grid), np.max(lat_grid), 0.1)
    target_lon_grid, target_lat_grid = np.meshgrid(target_lon, target_lat)
    
    # 5. Interpolation with fallback mechanism (Linear -> Nearest)
    # Assuming processing u_wind (taking u component as an example)
    u_key = 'uas' if 'uas' in ds else 'u10' 
    u_data = ds[u_key].values[0] # Take the first time step as an example
    
    try:
        # Prioritize linear interpolation
        u_interp = griddata((lon_grid.flatten(), lat_grid.flatten()), 
                            u_data.flatten(), 
                            (target_lon_grid, target_lat_grid), 
                            method='linear')
    except Exception:
        # Fallback to nearest neighbor if linear interpolation fails due to sparse points
        print("⚠️ Linear interpolation failed, automatically falling back to nearest neighbor.")
        u_interp = griddata((lon_grid.flatten(), lat_grid.flatten()), 
                            u_data.flatten(), 
                            (target_lon_grid, target_lat_grid), 
                            method='nearest')
                            
    return target_lon_grid, target_lat_grid, u_interp
