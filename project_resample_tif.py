import rasterio
from rasterio.warp import reproject
from rasterio.enums import Resampling
import os
from tqdm import tqdm  # 引入tqdm库

# 指定源栅格数据
source_raster = 'F:/Jingyi/Climate/Dismo/output_1990_2022_WGS84_Albert/biovar_1_1990_WGS84.tif'

# 目标文件夹路径
target_folder = 'F:/Jingyi/Climate/Dismo/output_prediction_test'

def update_crs_for_folder(source_raster, target_folder):
    # 读取源栅格数据的CRS及其它参数
    with rasterio.open(source_raster) as rst:
        source_crs = rst.crs
        source_transform = rst.transform
        source_height = rst.height
        source_width = rst.width
        meta = rst.meta.copy()
    
    # 获取目标文件夹中所有tif文件
    tif_files = [f for f in os.listdir(target_folder) if f.endswith('.tif')]
    
    # 遍历目标文件夹中的所有tif文件
    for filename in tqdm(tif_files, desc="Reprojecting rasters"):  # 使用tqdm添加进度条
        file_path = os.path.join(target_folder, filename)
        
        with rasterio.open(file_path) as src:
            # 准备新的文件元数据
            kwargs = meta.copy()
            kwargs.update({
                'crs': source_crs,
                'transform': source_transform,
                'width': source_width,
                'height': source_height
            })
            
            new_file_path = file_path.replace('.tif', '_albert.tif')
            
            # 创建并写入新文件
            with rasterio.open(new_file_path, 'w', **kwargs) as dst:
                # 仅处理第一波段
                data = src.read(1)
                out_data = data.copy()
                reproject(
                    source=data,
                    destination=out_data,
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=source_transform,
                    dst_crs=source_crs,
                    resampling=Resampling.bilinear
                )
                dst.write(out_data, 1)

# 执行函数
update_crs_for_folder(source_raster, target_folder)
