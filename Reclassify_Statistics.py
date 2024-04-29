# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 10:36:51 2024

@author: s224016798
"""

import rasterio
import numpy as np
import pandas as pd
import glob
import os

def calculate_area_for_class_1(raster_path, pixel_area):
    """
    计算栅格数据中分类为1的面积。

    参数:
    - raster_path: 栅格数据文件的路径。
    - pixel_area: 每个像素代表的实际面积（单位与你想要的面积单位相同，例如平方米）。

    返回:
    - 分类为1的总面积。
    """
    with rasterio.open(raster_path) as src:
        raster = src.read(1)  # 读取第一个波段

    counts = np.sum((raster == 1).astype(np.int64))
    area = counts * pixel_area
    return area

def process_folder(folder_path, pixel_area):
    """
    处理指定文件夹内的所有栅格数据文件，计算分类为1的面积。

    参数:
    - folder_path: 包含栅格数据文件的文件夹路径。
    - pixel_area: 每个像素代表的实际面积。

    输出:
    - 一个CSV文件，包含每个文件的分类为1的面积。
    """
    # 获取文件夹内所有.tif文件的路径
    raster_files = glob.glob(os.path.join(folder_path,'*.tif'))
    
    # 准备一个DataFrame来存储结果
    results = pd.DataFrame(columns=['Year', 'Area'])

    for file_path in raster_files:
        # 假设文件名格式为 "landuse_YEAR.tif"
        filename = os.path.basename(file_path)
        year = filename.split('_')[2]
        area = calculate_area_for_class_1(file_path, pixel_area)
        # 使用pd.concat代替.append
        new_row = pd.DataFrame({'Year': [year], 'Area': [area]})
        results = pd.concat([results, new_row], ignore_index=True)
        #results = results.append({'Year': year, 'Area': area}, ignore_index=True)
    
    # 排序并重置索引
    results.sort_values(by='Year', inplace=True)
    results.reset_index(drop=True, inplace=True)

    # 输出到CSV文件
    results.to_csv('F:/Jingyi/CLCD/cropland_areas.csv', index=False)
    print("Results saved to cropland_areas.csv")

# 使用示例
folder_path = 'F:/Jingyi/CLCD/OriginalData'
pixel_area = 900  # 假设每个像素代表900平方米
process_folder(folder_path, pixel_area)