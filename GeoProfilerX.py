"""
GeoProfilerX
============

A Python tool for extracting line and swath profiles from
projected single-band raster datasets using LineString and
MultiLineString vector geometries.

Supported raster applications
-----------------------------
• Digital Elevation Models (DEM)
• InSAR displacement products
• Gravity and magnetic anomaly rasters
• Terrain derivatives
• Geophysical raster datasets
• Environmental and climate rasters
• Vegetation indices (e.g., NDVI)
• Any projected single-band raster dataset

Features
--------
• Line and swath profile extraction
• Automatic CRS validation and reprojection
• Publication-quality profile plots (PNG & PDF)
• Input data preview with profile overlay
• CSV export of sampled profile values with X/Y coordinates
• Export sampled profile points to ESRI Shapefile and GeoPackage formats
• Organized output directories (csv, geopackage, pdf, png, shapefiles)
• Supports LineString and MultiLineString geometries
• Works with any projected single-band raster

Author
------
Chandni Verma

License
-------
MIT License

GitHub
------
https://github.com/chandnivermageo/GeoProfilerX
"""

# =====================================================
# USER SETTINGS
# =====================================================

profile_type = "line"      # "line" or "swath"
swath_width = 600          # Swath width (metres)
smooth_sigma = 5           # Gaussian smoothing (0 = disabled)

raster_name = "Raster"     # e.g. Elevation, Displacement, NDVI
raster_unit = "Value"      # e.g. m, mm, dB, °C, mGal

remove_outliers = False    # Remove abrupt spikes before smoothing

raster_path = r"/path/to/raster.tif"
line_path = r"/path/to/profile.shp"


# =====================================================
# GeoProfilerX
# =====================================================

def run_geoprofilerx():
    import os
    import time
    
    import numpy as np
    import rasterio
    import geopandas as gpd
    import pandas as pd
    
    import matplotlib
    import matplotlib.pyplot as plt
    
    from scipy.ndimage import gaussian_filter1d
    from shapely.geometry import LineString, MultiLineString, box
    
    
    # =====================================================
    # INITIALIZATION
    # =====================================================
    
    os.makedirs("outputs", exist_ok=True)
    
    os.makedirs("outputs/csv", exist_ok=True)
    os.makedirs("outputs/geopackage", exist_ok=True)
    os.makedirs("outputs/pdf", exist_ok=True)
    os.makedirs("outputs/png", exist_ok=True)
    os.makedirs("outputs/shapefiles", exist_ok=True)
    
    start_time = time.time()
    
    
    # =====================================================
    # MATPLOTLIB CONFIGURATION
    # =====================================================
    
    # Embed editable fonts in exported PDF and PS figures
    matplotlib.rcParams["pdf.fonttype"] = 42
    matplotlib.rcParams["ps.fonttype"] = 42
    
    
    # =====================================================
    # VALIDATE INPUT DATA
    # =====================================================
    
    if profile_type not in ["line", "swath"]:
        raise ValueError(
            f"Invalid profile_type: '{profile_type}'. "
            "Expected 'line' or 'swath'."
        )
    
    # -----------------------------------------------------
    # Load the raster dataset
    # -----------------------------------------------------
    
    src = rasterio.open(raster_path)
    
    dx = abs(src.res[0])
    dy = abs(src.res[1])
    
    if src.crs is None:
        raise ValueError(
            "Raster has no Coordinate Reference System (CRS)."
        )
    
    # Profile distances require projected coordinates
    if src.crs.is_geographic:
        raise ValueError(
            "Raster is in a Geographic CRS.\n"
            "Please project the raster (e.g., UTM) before running GeoProfiler."
        )
    
    # Only single-band rasters are supported
    if src.count != 1:
        raise ValueError(
            f"Expected a single-band raster, but found {src.count} bands."
        )
    
    # -----------------------------------------------------
    # Load the profile geometries
    # -----------------------------------------------------
    
    gdf = gpd.read_file(line_path)
    
    if gdf.empty:
        raise ValueError(
            "Input vector file contains no features."
        )
    
    if gdf.crs is None:
        raise ValueError(
            "Input vector has no Coordinate Reference System (CRS)."
        )
    
    supported = {"LineString", "MultiLineString"}
    
    if not any(g in supported for g in gdf.geom_type.unique()):
        raise ValueError(
            "Input vector must contain LineString or "
            "MultiLineString geometries."
        )
    
    print(f"Raster CRS : {src.crs}")
    print(f"Vector CRS : {gdf.crs}")
    
    # Reproject the vector so both datasets share the same CRS
    if gdf.crs != src.crs:
        gdf = gdf.to_crs(src.crs)
        print("Vector reprojected to match raster CRS")
    
    # Ensure at least one profile intersects the raster extent
    raster_extent = box(*src.bounds)
    
    if not gdf.intersects(raster_extent).any():
        raise ValueError(
            "Input profile does not overlap the raster extent. "
            "Please check that you selected the correct raster and vector files."
        )
    
    
    # =====================================================
    # INPUT DATA PREVIEW
    # =====================================================
    
    print("Generating input data preview...")
    
    raster_data = src.read(1, masked=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Recommended Color Scheme
    # Spectral_r  -> InSAR, displacement
    # terrain     -> DEM
    # RdYlBu_r    -> General scientific rasters
    
    image = ax.imshow(
        raster_data,
        cmap="Spectral_r",     # RdYlBu_r, Spectral_r, terrain
        extent=[
            src.bounds.left,
            src.bounds.right,
            src.bounds.bottom,
            src.bounds.top,
        ],
        origin="upper"
    )
    
    gdf.plot(
        ax=ax,
        color="black",
        linewidth=1.5,
        label="Profile Line",
    )
    
    cbar = plt.colorbar(
        image,
        ax=ax,
        shrink=0.8,
    )
    
    cbar.set_label(
        f"{raster_name} ({raster_unit})"
    )
    
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    
    ax.set_title(
        f"Input Data Preview – {raster_name}"
    )
    
    ax.legend()
    
    plt.tight_layout()
    
    
    # Export the preview figure
    base = raster_name.lower().replace(" ", "_")
    
    plt.savefig(
        f"outputs/pdf/{base}_input_preview.pdf",
        transparent=True,
        bbox_inches="tight",
    )
    
    plt.savefig(
        f"outputs/png/{base}_input_preview.png",
        dpi=300,
        bbox_inches="tight",
    )
    
    plt.show()
    plt.close()
    
    print("Input data preview generated.")
    
    
    # =====================================================
    # RASTER SAMPLING
    # =====================================================
    
    def sample_values(coords):
    
        vals = np.array(
            [v[0] for v in src.sample(coords)],
            dtype=float,
        )
    
        if src.nodata is not None:
            vals[vals == src.nodata] = np.nan
    
        if remove_outliers:
            diff = np.abs(np.diff(vals, prepend=vals[0]))
            thr = np.nanpercentile(diff, 95)
            vals[diff > thr] = np.nan
    
        mask = np.isnan(vals)
    
        if np.any(mask) and np.sum(~mask) > 1:
            vals[mask] = np.interp(
                np.flatnonzero(mask),
                np.flatnonzero(~mask),
                vals[~mask],
            )
    
        if smooth_sigma > 0:
            vals = gaussian_filter1d(
                vals,
                sigma=smooth_sigma,
            )
    
        return vals
    
    
    # =====================================================
    # PROFILE EXTRACTION
    # =====================================================
    
    profiles_generated = 0
    
    for idx, geom in enumerate(gdf.geometry):
    
        if isinstance(geom, MultiLineString):
            print(
                f"Feature {idx + 1}: MultiLineString detected "
                f"({len(geom.geoms)} parts). "
                "Using the longest line."
            )
            line = max(geom.geoms, key=lambda g: g.length)
    
        elif isinstance(geom, LineString):
            line = geom
    
        else:
            continue
    
        print(f"Processing profile {idx + 1}")
    
        # Skip profiles shorter than two raster pixels
        if line.length < (2 * dx):
            print(
                f"Skipping profile {idx + 1}: "
                "Length is less than two raster pixels."
            )
            continue
    
        distances = np.arange(0, line.length, dx)
    
        # Ensure the profile endpoint is included
        if len(distances) == 0 or distances[-1] < line.length:
            distances = np.append(distances, line.length)
    
        pts = [line.interpolate(d) for d in distances]
    
        dist_km = distances / 1000
    
        # -----------------------------------------------------
        # LINE PROFILE EXTRACTION
        # -----------------------------------------------------
    
        if profile_type == "line":
    
            coords = [(p.x, p.y) for p in pts]
            profile = sample_values(coords)
    
            if np.all(np.isnan(profile)):
                print(
                    f"Skipping profile {idx + 1}: "
                    "All sampled values are NoData."
                )
                continue
    
            plt.figure(figsize=(8, 3))
            ax = plt.gca()
    
            ax.grid(
                True,
                color="0.92",      # light gray
                linewidth=1.0,
                linestyle="-",
            )
    
            ax.set_axisbelow(True)
    
            for spine in ax.spines.values():
                spine.set_linewidth(0.8)
    
            ax.tick_params(
                direction="in",
                color="0.66",
                top=True,
                right=True,
                bottom=True,
                left=True,
                length=4,
                width=1.0,
            )
    
            plt.plot(
                dist_km,
                profile,
                color="black",
                lw=1.4,
            )
            plt.xlabel("Distance (km)")
            plt.ylabel(f"{raster_name} ({raster_unit})")
            plt.title(f"{raster_name} - Line Profile {idx + 1}")
    
            plt.tight_layout()
    
            plt.savefig(
                f"outputs/pdf/{base}_line_{idx + 1}.pdf",
                transparent=True,
                bbox_inches="tight",
            )
    
            plt.savefig(
                f"outputs/png/{base}_line_{idx + 1}.png",
                dpi=300,
                bbox_inches="tight",
            )
    
            # Export Line Profile to CSV
            line_df = pd.DataFrame(
                {
                    "X_Cor": [p.x for p in pts],
                    "Y_Cor": [p.y for p in pts],
                    "Dist_km": dist_km,
                    f"{raster_name}_{raster_unit}": profile,
                }
            )
    
            line_df.to_csv(
                f"outputs/csv/{base}_line_{idx + 1}.csv",
                index=False,
            )
    
            # -------------------------------------------------
            # GeoPackage
            # -------------------------------------------------
            line_gdf = gpd.GeoDataFrame(
                line_df.copy(),
                geometry=gpd.points_from_xy(
                    line_df["X_Cor"],
                    line_df["Y_Cor"],
                ),
                crs=src.crs,
            )
    
            line_gdf.to_file(
                os.path.join(
                    "outputs",
                    "geopackage",
                    f"{base}_line_{idx + 1}.gpkg",
                ),
                layer=f"{base}_line_{idx + 1}",
                driver="GPKG",
            )
    
            # -------------------------------------------------
            # Shapefile
            # -------------------------------------------------
            line_shp = line_gdf.rename(
                columns={
                    f"{raster_name}_{raster_unit}": "Value",
                }
            ).copy()
    
            line_shp.to_file(
                f"outputs/shapefiles/{base}_line_{idx + 1}.shp"
            )
            profiles_generated += 1
    
            plt.show()
            plt.close()
    
        else:
    
            # -----------------------------------------------------
            # SWATH PROFILE EXTRACTION
            # -----------------------------------------------------
    
            offsets = np.arange(
                -swath_width / 2,
                swath_width / 2 + dy,
                dy,
            )
    
            stack = []
    
            for off in offsets:
    
                coords = []
    
                for i, p in enumerate(pts):
    
                    if i == 0:
                        p1, p2 = pts[i], pts[i + 1]
    
                    elif i == len(pts) - 1:
                        p1, p2 = pts[i - 1], pts[i]
    
                    else:
                        p1, p2 = pts[i - 1], pts[i + 1]
    
                    tx = p2.x - p1.x
                    ty = p2.y - p1.y
    
                    L = np.hypot(tx, ty)
    
                    if L == 0:
                        coords.append((p.x, p.y))
                        continue
    
                    # Compute the unit normal vector for swath offsets
                    tx /= L
                    ty /= L
    
                    nx = -ty
                    ny = tx
    
                    coords.append(
                        (
                            p.x + off * nx,
                            p.y + off * ny,
                        )
                    )
    
                stack.append(sample_values(coords))
    
            stack = np.array(stack)
    
            if np.all(np.isnan(stack)):
                print(
                    f"Skipping profile {idx + 1}: "
                    "All sampled values are NoData."
                )
                continue
    
            rmin = np.nanmin(stack, axis=0)
            rmean = np.nanmean(stack, axis=0)
            rmax = np.nanmax(stack, axis=0)
    
            plt.figure(figsize=(8, 3))
            ax = plt.gca()
    
            ax.grid(
                True,
                color="0.92",
                linewidth=1.0,
                linestyle="-",
            )
    
            ax.set_axisbelow(True)
    
            for spine in ax.spines.values():
                spine.set_linewidth(0.8)
    
            ax.tick_params(
                direction="in",
                color="0.66",
                top=True,
                right=True,
                bottom=True,
                left=True,
                length=4,
                width=1.0,
            )
    
            plt.fill_between(
                dist_km,
                rmin,
                rmax,
                color="lightgray",
                alpha=0.4,
                label="Min-Max",
            )
    
            plt.plot(
                dist_km,
                rmean,
                lw=1.3,
                color="black",
                label="Mean",
            )
            plt.xlabel("Distance (km)")
            plt.ylabel(f"{raster_name} ({raster_unit})")
            plt.title(f"{raster_name} - Swath Profile {idx + 1}")
    
            plt.legend()
            plt.tight_layout()
    
            plt.savefig(
                f"outputs/pdf/{base}_swath_{idx + 1}.pdf",
                transparent=True,
                bbox_inches="tight",
            )
            plt.savefig(
                f"outputs/png/{base}_swath_{idx + 1}.png",
                dpi=300,
                bbox_inches="tight",
            )
    
            # Export Swath Profile to CSV
            swath_df = pd.DataFrame(
                {
                    "X_Cor": [p.x for p in pts],
                    "Y_Cor": [p.y for p in pts],
                    "Dist_km": dist_km,
                    f"Minimum_{raster_name}_{raster_unit}": rmin,
                    f"Mean_{raster_name}_{raster_unit}": rmean,
                    f"Maximum_{raster_name}_{raster_unit}": rmax,
                }
            )
    
            swath_df.to_csv(
                f"outputs/csv/{base}_swath_{idx + 1}.csv",
                index=False,
            )
    
            # -------------------------------------------------
            # GeoPackage
            # -------------------------------------------------
            swath_gdf = gpd.GeoDataFrame(
                swath_df.copy(),
                geometry=gpd.points_from_xy(
                    swath_df["X_Cor"],
                    swath_df["Y_Cor"],
                ),
                crs=src.crs,
            )
    
            swath_gdf.to_file(
                os.path.join(
                    "outputs",
                    "geopackage",
                    f"{base}_swath_{idx + 1}.gpkg",
                ),
                layer=f"{base}_swath_{idx + 1}",
                driver="GPKG",
            )
    
            # -------------------------------------------------
            # Shapefile
            # -------------------------------------------------
            swath_shp = swath_gdf.rename(
                columns={
                    f"Minimum_{raster_name}_{raster_unit}": "Minimum",
                    f"Mean_{raster_name}_{raster_unit}": "Mean",
                    f"Maximum_{raster_name}_{raster_unit}": "Maximum",
                }
            ).copy()
    
            swath_shp.to_file(
                f"outputs/shapefiles/{base}_swath_{idx + 1}.shp"
            )
    
            profiles_generated += 1
    
            plt.show()
            plt.close()
    
    
    # =====================================================
    # EXECUTION SUMMARY
    # =====================================================
    
    elapsed_time = time.time() - start_time
    
    print("\n-----------------------------------")
    print("GeoProfiler Execution Summary")
    print("-----------------------------------")
    print(f"Raster size        : {src.width} × {src.height} pixels")
    
    print(f"Raster resolution  : {dx:.2f} × {dy:.2f} m")
    print(f"Profiles processed : {len(gdf)}")
    print(f"Profiles generated : {profiles_generated}")
    print(f"Profile type       : {profile_type.capitalize()}")
    print(f"Execution time     : {elapsed_time:.2f} s")
    print("Outputs saved in   : outputs/ csv | geopackage | pdf | png | shapefiles")
    print("-----------------------------------")
    
    src.close()


# =====================================================
# STANDALONE EXECUTION
# =====================================================

if __name__ == "__main__":
    run_geoprofilerx()
