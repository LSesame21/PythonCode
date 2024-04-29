# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:04:03 2024

@author: s224016798
"""

import rasterio
import os

# 指定源栅格数据（我们将从这个文件获取坐标系）
source_raster = 'F:/Jingyi/Climate/ChinaDataset/prelzw/pre_1991.tif'

# 目标文件夹路径
target_folder = 'F:/Jingyi/Climate/Dismo/output_1990_2022'

def update_crs_for_folder(source_raster, target_folder):
    # 读取源栅格数据的CRS
    with rasterio.open(source_raster) as src:
        source_crs = src.crs

    # 遍历目标文件夹中的所有tif文件
    for filename in os.listdir(target_folder):
        if filename.endswith('.tif'):
            # 完整的文件路径
            file_path = os.path.join(target_folder, filename)
            
            # 读取文件，更新CRS，并写入新文件
            with rasterio.open(file_path) as src:
                # 复制原文件的元数据
                kwargs = src.meta.copy()
                # 更新CRS
                kwargs.update({'crs': source_crs})
                
                # 定义新的文件名（为了安全，不直接覆盖原文件）
                new_file_path = file_path.replace('.tif', '_WGS84.tif')
                
                # 写入新文件
                with rasterio.open(new_file_path, 'w', **kwargs) as dst:
                    dst.write(src.read())

# 执行函数
update_crs_for_folder(source_raster, target_folder)
