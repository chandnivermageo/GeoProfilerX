# GeoProfilerX
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)

<p align="center">
  <img src="images/geoprofilerx_preview.png" width="100%">
</p>

GeoProfilerX is an open-source Python tool for extracting **line** and **swath profiles** from **projected single-band raster datasets** using **LineString** and **MultiLineString** vector geometries. It is designed for topographic, geophysical, remote sensing, environmental, and other geospatial applications, producing publication-quality profile visualizations and GIS-ready outputs for further analysis.

## Project Evolution

GeoProfilerX is the next-generation evolution of my earlier **GeoProfiler** project.

While GeoProfiler was developed specifically for extracting topographic profiles from Digital Elevation Models (DEMs), GeoProfilerX extends the concept into a general-purpose raster profiling tool capable of extracting both **line** and **swath profiles** from a broad range of **projected single-band raster datasets**, including DEMs, InSAR displacement products, gravity and magnetic anomalies, terrain derivatives, environmental rasters, vegetation indices, and other geospatial datasets.

Compared with the original GeoProfiler, GeoProfilerX introduces:

- Compatibility with a broad range of projected single-band raster datasets
- Improved input validation, CRS handling, and error checking
- Publication-quality line and swath profile plots (PNG & PDF)
- CSV export of sampled profile values with X/Y coordinates
- Export sampled profile points with profile attributes to ESRI Shapefile and GeoPackage formats
- Organized output directories
- Execution summaries and processing statistics

--- 

GeoProfilerX provides a simple workflow for extracting publication-ready profiles from projected raster datasets while automatically handling common geospatial preprocessing tasks.

## Features

- Extract **line profiles** from projected raster datasets
- Extract **swath profiles** with user-defined swath width
- Supports LineString and MultiLineString vector geometries
- Automatic CRS validation and vector reprojection
- Validates raster overlap before processing
- Handles NoData values and optional profile smoothing
- Publication-quality line and swath profile plots (PNG & PDF)
- CSV export of sampled profile values with X/Y coordinates
- Export sampled profile points to ESRI Shapefile and GeoPackage formats
- Input data preview with raster and profile overlay
- Organized output directories (CSV, GeoPackage, PDF, PNG, Shapefiles)
- Execution summary with processing statistics

---

## Supported Raster Types

GeoProfilerX works with a broad range of **projected single-band raster**, including:

- Digital Elevation Models (DEM)
- Gravity anomaly datasets
- Magnetic anomaly datasets
- InSAR displacement products
- Terrain derivatives
- Geophysical rasters
- Environmental and climate rasters
- Vegetation indices (e.g., NDVI)
- Other projected single-band raster datasets

---

## Requirements

- Python 3.10+

### Python Packages

- numpy
- scipy
- pandas
- matplotlib
- rasterio
- geopandas
- shapely

Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## Input Requirements

### Raster

- Single-band raster
- Projected Coordinate Reference System (e.g., UTM)
- Raster format readable by Rasterio/GDAL (e.g., `.tif`, `.img`)

> The raster must contain valid georeferencing and CRS information. NoData values should be properly defined in the raster metadata when applicable.

### Vector

- LineString or MultiLineString geometries
- Supported formats: ESRI Shapefile (`.shp`, `.shx`, `.dbf`, `.prj`) or GeoJSON (`.geojson`, `.json`)
- Vector dataset must have a defined CRS; it is automatically reprojected to match the raster CRS if necessary

> All required Shapefile components must be provided together. The `.prj` file is required for CRS detection.

---

## Outputs

For each extracted profile, GeoProfilerX generates:

- Input data preview (PNG & PDF)
- Publication-quality line and swath profile plots (PNG & PDF)
- CSV export of sampled profile values with X/Y coordinates
- Export sampled points with attributes to ESRI Shapefile and GeoPackage formats

An execution summary is also printed after processing.

---

## Output Directory Structure

Generated outputs are automatically organized into dedicated directories:

```text
outputs/
├── csv/
├── geopackage/
├── pdf/
├── png/
└── shapefiles/
```

---

## Example Workflow

1. Specify the input raster and vector paths.

```python
raster_path = "sample_raster.tif"
line_path = "profiles.shp"
```

2. Select the profile type.

```python
profile_type = "line"
```

or

```python
profile_type = "swath"
```

3. Run the script.

Generated outputs are automatically organized into dedicated subdirectories within the outputs/ folder.

---

## Repository Structure

```
GeoProfilerX/
├── GeoProfilerX.py
├── GeoProfilerX.ipynb
├── README.md
├── requirements.txt
├── CITATION.cff
├── LICENSE
└── images/
```

---

## Future Development

Planned enhancements include:

- Interactive profile drawing
- Batch processing of multiple profile files
- Multi-raster profile extraction

---

## License

This project is licensed under the MIT License.

---

## Author

**Chandni Verma**

LinkedIn: <https://www.linkedin.com/in/chandni-verma-geo>

GitHub: <https://github.com/chandnivermageo>

---

## Citation

If you use GeoProfilerX in your research, please cite this repository.

```

Verma, C. (2026). GeoProfilerX: A Python tool for extracting line and swath profiles from projected raster datasets. GitHub repository. https://github.com/chandnivermageo/GeoProfilerX

```
