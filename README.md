# CMIP6_SIC_Evaluation
CMIP6 Sea Ice Concentration Evaluation and Wind Field Processing Pipeline
# CMIP6 Sea Ice & Wind Field Evaluation Pipeline for Greenland Fjords

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![xarray](https://img.shields.io/badge/powered_by-xarray-green.svg)](http://xarray.pydata.org/)
[![Cartopy](https://img.shields.io/badge/mapping-Cartopy-orange.svg)]()

## 📌 Project Overview
This repository contains a robust, end-to-end data processing and visualization pipeline designed to evaluate Earth System Models (ESMs) — specifically **CESM2** and **HadGEM3-GC3.1** — in simulating Sea Ice Concentration (SIC) and Wind Fields in the Greenland Fjord regions. 

The pipeline processes both **historical (1980-2014)** and **future scenario (2015-2100)** CMIP6 outputs, comparing them against observational datasets. Beyond basic extraction, it explicitly tackles severe data heterogeneity, including non-standard calendar harmonization, spatial grid misalignment, and wind field circular artifacts. This codebase serves as the foundational data infrastructure for my proposed PhD research on AI-driven bias correction for regional ocean/climate models.

## 🚀 Core Technical Challenges & Solutions
Processing multi-source polar climate data involves unique bottlenecks. This pipeline implements custom, resilient solutions strictly based on real-world data anomalies:

### 1. Resilient Temporal Harmonization (`cftime` Handling)
- **The Challenge**: ESMs utilize non-standard calendars (e.g., `360_day`, `noleap`), causing standard `datetime` parsing to crash on dates like Feb 29th or Dec 31st.
- **The Solution**: Developed a custom time-bound correction function that dynamically detects calendar types, maps illegal dates (e.g., converting `12-31` to `12-30` for 360-day calendars), and guarantees 100% temporal alignment without data loss.

### 2. Wind Field Processing & Artifact Mitigation
- **The Challenge**: Raw wind field data often suffers from circular artifacts at the boundaries and inconsistent coordinate naming conventions (`lon` vs `longitude`).
- **The Solution**: Implemented `process_single_decade_wind_data` which:
  - Dynamically identifies coordinate keys to prevent `KeyError`.
  - Converts `0-360` longitudes to `-180-180` on the fly.
  - Prioritizes original wind grids to avoid forced interpolation, significantly reducing circular artifacts in the final vector fields.

### 3. Smart Spatial Interpolation & Grid Alignment
- **The Challenge**: Models and observations have mismatched spatial dimensions and curvilinear grids.
- **The Solution**: 
  - Built an automated `np.meshgrid` dimension checker to dynamically align 1D/2D lat/lon arrays.
  - Utilized `scipy.interpolate.griddata` with a **fallback mechanism**: if linear interpolation fails due to sparse data points, it automatically degrades to `nearest` neighbor interpolation to prevent pipeline crashes.
  - Applied strict spatial masking (e.g., SIC < 15% defined as ice-free) to isolate valid fjord geometries.

### 4. Bulletproof Pipeline Execution
- Handled `NaN` propagation safely during model inter-comparisons (`np.where(np.isnan(...))`).
- Implemented dynamic file path parsing (`os.path.basename`, `os.path.join`) to automatically extract model names (CESM2/HadGEM3) and safely export results, eliminating hardcoded path errors.

## 📊 Publication-Quality Visualization Module
A major focus of this pipeline is generating paper-ready figures directly from the processed data, adhering to strict academic publishing standards:
- **Academic Styling**: Configured global `matplotlib` parameters (Arial font, inward ticks, top/right tick visibility, `seaborn-v0_8-whitegrid` style).
- **Geospatial Mapping**: Utilized `cartopy` to add high-resolution coastlines and land features (`cfeature.COASTLINE`, `cfeature.LAND`) with precise z-order layering.
- **Customized Layouts**: Engineered complex multi-panel layouts using `fig.add_axes` and customized horizontal colorbars with precise label padding and semantic bold fonts.

## 🔄 Pipeline Architecture

```text
[Raw NetCDF Data] (CMIP6 Historical/Future SIC + Wind Fields + Obs)
       │
       ▼
1. Ingestion & Dynamic Variable Detection (xarray)
       │
       ▼
2. Temporal Harmonization (cftime boundary correction)
       │
       ▼
3. Spatial Alignment (Meshgrid validation & 0-360 to -180-180 conversion)
       │
       ▼
4. Advanced Interpolation (griddata with linear-to-nearest fallback)
       │
       ▼
5. Physical Masking (SIC < 15% thresholding & Wind artifact removal)
       │
       ▼
6. Statistical Aggregation (Decadal means: 1980s, 1990s, 2000s, Future)
       │
       ▼
7. Publication Plotting (Cartopy mapping & multi-panel rendering)


🛠️ Environment & Dependencies
Data Manipulation: xarray, numpy, pandas
Geospatial & Mapping: cartopy (coastlines, land features, projections)
Interpolation & Math: scipy (griddata), cftime
Visualization: matplotlib (custom academic styling)
🔮 Future Work & Connection to PhD Research
While this pipeline successfully quantifies baseline model biases and wind-driven sea ice dynamics in complex fjord topographies, traditional statistical methods struggle with the non-linear, spatially heterogeneous errors inherent in coarse-resolution ESMs.

In my proposed PhD research, I aim to extend this exact pipeline by integrating Deep Learning architectures (e.g., CNNs, Graph Neural Networks) to:

Learn the non-linear mapping between coarse CMIP6 outputs and high-resolution coastal observations.
Develop an AI-driven surrogate model to dynamically correct SIC and wind field biases in real-time.
Quantify the epistemic and aleatoric uncertainties of the AI-corrected Earth System Models.
📂 Repository Structure
├── data_analyse.py        # Core pipeline: Ingestion, cftime fixing, spatial masking
├── wind_processing.py     # Wind field artifact mitigation and grid alignment
├── visualization.py       # Publication-ready plotting (Cartopy, academic styling)
├── utils/                 # Modularized functions for interpolation and metrics
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation


📫 Contact
Xinyu Guo
Prospective PhD Candidate in Marine AI & Earth System Modeling
📧 Email: 15021099770@163.com
🔗 [Your LinkedIn Profile] | 
