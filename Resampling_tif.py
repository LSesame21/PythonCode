import os
import rasterio
from rasterio.warp import reproject, Resampling
from tqdm import tqdm  # Import tqdm for progress bar functionality

def resample_rasters(input_folder, output_folder, new_cell_size=1000):
    # List all TIFF files in the input directory
    tif_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]
    
    # Initialize a progress bar
    pbar = tqdm(tif_files, desc='Resampling Rasters')

    for filename in pbar:
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, f'resampled_1000m_{filename}')
        
        with rasterio.open(input_path) as src:
            old_crs = src.crs
            old_transform = src.transform
            
            # Calculate the dimensions of the new raster
            new_width = int((src.bounds.right - src.bounds.left) / new_cell_size)
            new_height = int((src.bounds.top - src.bounds.bottom) / new_cell_size)
            
            # Define new transformation
            new_transform = rasterio.Affine(new_cell_size, old_transform.b, src.bounds.left,
                                            old_transform.d, -new_cell_size, src.bounds.top)

            # Set output file metadata
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': old_crs,
                'transform': new_transform,
                'width': new_width,
                'height': new_height
            })
            
            # Create and write resampled data to the output file
            with rasterio.open(output_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):  # Process each band
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=old_crs,
                        dst_transform=new_transform,
                        dst_crs=old_crs,
                        resampling=Resampling.bilinear  # Choose different resampling methods if needed
                    )

if __name__ == "__main__":
    input_folder = 'F:/Jingyi/Climate/Dismo/output_prediction_WGS84_Albert'  # Specify input folder
    output_folder = 'F:/Jingyi/Climate/Dismo/output_prediction_1000m'  # Specify output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    resample_rasters(input_folder, output_folder, new_cell_size=1000)
