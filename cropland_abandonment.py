# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 10:53:11 2024

@author: s224016798
"""

from osgeo import gdal
import numpy as np
from tqdm import tqdm  # 导入tqdm

def load_raster(file_path):
    """加载栅格数据并返回 numpy 数组"""
    dataset = gdal.Open(file_path)
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    return array, dataset.GetGeoTransform(), dataset.GetProjection()

def identify_fallow_land(start_year_data, following_years_data, previous_fallow=None):
    """识别撂荒地并返回一个标记了撂荒耕地的数组"""
    # 第一种情况：第一年为耕地且接下来两年地类编码均为 0
    fallow_case1 = (start_year_data == 1) & (following_years_data[0] == 0) & (following_years_data[1] == 0)

    # 第二种情况：连续三年地类编码均为 0
    fallow_case2 = (start_year_data == 0) & (following_years_data[0] == 0) & (following_years_data[1] == 0)

    # 标记撂荒耕地为 11
    fallow_land = np.zeros_like(start_year_data, dtype=np.uint8)
    fallow_land[fallow_case1] = 11

    # 如果上一年被判定为撂荒耕地，则继续标记为 11
    if previous_fallow is not None:
        fallow_land[fallow_case2 & (previous_fallow == 11)] = 11

    return fallow_land

# 加载每年的数据
yearly_data = []
geotransforms = []
projections = []
for year in tqdm(range(1994, 1997), desc="加载数据"):  # 添加进度条
    data, geotransform, projection = load_raster(f'F:/Jingyi/CLCD/Reclassify/CLCD_Reclassified_{year}.tif')
    yearly_data.append(data)
    geotransforms.append(geotransform)
    projections.append(projection)

# 初始化前一年的撂荒数据为 None
previous_fallow = None

# 逐年识别撂荒地并保存结果
for i in tqdm(range(len(yearly_data) - 2), desc="处理撂荒地"):  # 添加进度条
    fallow_land = identify_fallow_land(yearly_data[i], yearly_data[i+1:i+3], previous_fallow)
    previous_fallow = fallow_land  # 更新前一年的撂荒数据
    output_path = f'F:/Jingyi/CLCD/Fallowland/fallow_land_test_{1990+i}-{1991+i}-{1992+i}.tif'
    driver = gdal.GetDriverByName('GTiff')
    out_dataset = driver.Create(output_path, fallow_land.shape[1], fallow_land.shape[0], 1, gdal.GDT_UInt16)
    out_band = out_dataset.GetRasterBand(1)

    # 设置相同的地理坐标系和仿射变换参数
    out_dataset.SetGeoTransform(geotransforms[i])
    out_dataset.SetProjection(projections[i])
    out_band.WriteArray(fallow_land)
    out_band.FlushCache()
    out_dataset = None
    print(f"撂荒地识别完成，{1990+i}-{1991+i}-{1992+i}年的结果已保存到: {output_path}")
