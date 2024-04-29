# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:14:54 2024

@author: s224016798
"""

from osgeo import gdal
import numpy as np

def calculate_marked_area(file_path, pixel_value=11, pixel_area=900):
    """
    计算栅格数据中特定像素值的总面积。
    
    :param file_path: 栅格数据文件路径。
    :param pixel_value: 需要统计面积的像素值，默认为 11。
    :param pixel_area: 单个像素代表的实际面积（平方米），默认为 900（即 30m x 30m）。
    :return: 标记为特定像素值的总面积（平方米）。
    """
    # 加载栅格数据
    dataset = gdal.Open(file_path)
    if dataset is None:
        raise FileNotFoundError(f"File not found: {file_path}")
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    
    # 计算特定像素值的数量
    count = np.count_nonzero(array == pixel_value)
    
    # 计算总面积
    total_area = count * pixel_area
    return total_area

# 示例：计算标记为 11 的面积
file_path = 'F:/Jingyi/CLCD/Fallowland1/fallow_land_test_1993-1994-1995.tif'  # 更新为您的file path
marked_area = calculate_marked_area(file_path)
print(f"标记为 11 的总面积是：{marked_area} 平方米")
