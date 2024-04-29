# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 17:26:24 2024

@author: s224016798
"""

import rasterio
from rasterio.warp import calculate_default_transform, reproject
import os

def apply_projection_to_folder(source_folder, target_raster_path, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开目标影像b以获取其CRS
    with rasterio.open(target_raster_path) as target:
        target_crs = target.crs

    # 遍历源文件夹中的所有.tif文件
    for filename in os.listdir(source_folder):
        if filename.endswith('.tif'):
            source_raster_path = os.path.join(source_folder, filename)
            output_raster_path = os.path.join(output_folder, filename)

            # 打开源影像a
            with rasterio.open(source_raster_path) as src:
                src_meta = src.meta.copy()  # 复制源影像的元数据

                # 计算从源影像CRS到目标CRS的变换参数
                transform, width, height = calculate_default_transform(
                    src.crs, target_crs, src.width, src.height, *src.bounds)
                
                # 更新元数据以包括新的投影、变换参数和尺寸
                src_meta.update({
                    'crs': target_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })

                # 写入具有新投影的输出影像
                with rasterio.open(output_raster_path, 'w', **src_meta) as dst:
                    for band in range(1, src.count + 1):
                        # 从源影像到目标影像的重投影
                        reproject(
                            source=rasterio.band(src, band),
                            destination=rasterio.band(dst, band),
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=target_crs,
                            resampling=rasterio.enums.Resampling.nearest)

                print(f"Projection added to {output_raster_path}")

# 设置源文件夹路径、目标影像b的路径和输出文件夹的路径
source_folder = r'F:\Jingyi\Climate\Dismo\output_1990_2022_WGS84'  # 源文件夹路径
target_raster_path = r'F:\Jingyi\CLCD\Fallowland_All\fallow_land_test_1990-1991-1992.tif'  # 影像b的路径
output_folder = r'F:\Jingyi\Climate\Dismo\output_1990_2022_WGS84_Albert'  # 输出文件夹路径

# 执行函数
apply_projection_to_folder(source_folder, target_raster_path, output_folder)



