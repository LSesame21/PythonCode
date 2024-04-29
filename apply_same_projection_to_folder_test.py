import rasterio
from rasterio.warp import calculate_default_transform, reproject
import os
from tqdm import tqdm  # Import tqdm for the progress bar

def apply_projection_to_folder(source_folder, target_raster_path, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the target raster to get its CRS
    with rasterio.open(target_raster_path) as target:
        target_crs = target.crs

    # List all .tif files in the source folder
    tif_files = [f for f in os.listdir(source_folder) if f.endswith('.tif')]
    
    # Initialize a progress bar
    pbar = tqdm(tif_files, desc="Applying Projection")

    # Iterate over all .tif files
    for filename in pbar:
        source_raster_path = os.path.join(source_folder, filename)
        output_raster_path = os.path.join(output_folder, filename)

        # Open the source raster
        with rasterio.open(source_raster_path) as src:
            src_meta = src.meta.copy()  # Copy metadata from the source raster

            # Calculate transformation parameters from source CRS to target CRS
            transform, width, height = calculate_default_transform(
                src.crs, target_crs, src.width, src.height, *src.bounds)
            
            # Update metadata to include the new projection, transformation parameters, and dimensions
            src_meta.update({
                'crs': target_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            # Write the output raster with the new projection
            with rasterio.open(output_raster_path, 'w', **src_meta) as dst:
                for band in range(1, src.count + 1):
                    # Reproject each band from the source raster to the target raster
                    reproject(
                        source=rasterio.band(src, band),
                        destination=rasterio.band(dst, band),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=target_crs,
                        resampling=rasterio.enums.Resampling.nearest)

            # Optional: update progress bar description with the filename being processed
            pbar.set_description(f"Processing {filename}")

# Set paths for source folder, target raster, and output folder
source_folder = r'F:\Jingyi\Climate\Dismo\output_prediction_WGS84'
target_raster_path = r'F:\Jingyi\Climate\Dismo\output_1990_2022_1000m\resampled_1000m_biovar_1_1990_WGS84.tif'
output_folder = r'F:\Jingyi\Climate\Dismo\output_prediction_WGS84_Albert'

# Execute the function
apply_projection_to_folder(source_folder, target_raster_path, output_folder)