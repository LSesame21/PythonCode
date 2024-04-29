# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 12:16:09 2024

@author: s224016798
"""

from osgeo import gdal
import numpy as np
from tqdm import tqdm○

def load_raster(file_path):
    """加载栅格数据并返回 numpy 数组"""
    dataset = gdal.Open(file_path)
    if dataset is None:
        raise FileNotFoundError(f"File not found: {file_path}")
    band = dataset.GetRasterBand(1)
    array = band.ReadAsArray()
    return array, dataset.GetGeoTransform(), dataset.GetProjection()

def identify_fallow_land(year, input_dir, output_dir):
    """针对指定年份，使用前一年的耕地撂荒判断数据进行撂荒地识别"""
    # 加载当前年份及前两年的数据
    data_current, geotransform, projection = load_raster(f'{input_dir}/CLCD_Reclassified_{year}.tif')
    data_prev1, _, _ = load_raster(f'{input_dir}/CLCD_Reclassified_{year-1}.tif')
    data_prev2, _, _ = load_raster(f'{input_dir}/CLCD_Reclassified_{year-2}.tif')
    
    # 加载上一年的撂荒判断结果，如果不存在则初始化为全0数组
    try:
        previous_fallow, _, _ = load_raster(f'{output_dir}/fallow_land_test_{year-3}-{year-2}-{year-1}.tif')
    except FileNotFoundError:
        previous_fallow = np.zeros_like(data_current, dtype=np.uint8)

    # 执行撂荒地识别
    fallow_land = np.zeros_like(data_current, dtype=np.uint8)
    fallow_case1 = (data_prev2 == 1) & (data_prev1 == 0) & (data_current == 0)
    fallow_case2 = (data_prev2 == 0) & (data_prev1 == 0) & (data_current == 0) & (previous_fallow == 11)
    fallow_land[fallow_case1 | fallow_case2] = 11

    # 保存结果
    output_path = f'{output_dir}/fallow_land_test_{year-2}-{year-1}-{year}.tif'
    driver = gdal.GetDriverByName('GTiff')
    options = ['COMPRESS=LZW']  # 使用LZW压缩
    out_dataset = driver.Create(output_path, fallow_land.shape[1], fallow_land.shape[0], 1, gdal.GDT_Byte, options=options)
    out_band = out_dataset.GetRasterBand(1)

    # 设置地理坐标系和仿射变换参数
    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(projection)
    out_band.WriteArray(fallow_land)
    out_band.FlushCache()
    out_dataset = None
    print(f"撂荒地识别完成，结果已保存到: {output_path}")
    
# 设置输入输出目录
input_dir = 'F:/Jingyi/CLCD/Reclassify1'
output_dir = 'F:/Jingyi/CLCD/Fallowland1'

# 对指定年份范围内的数据进行撂荒地识别
for year in tqdm(range(1992,2023), desc="处理撂荒地"): # 从1992年开始，确保有前两年的数据可用
    identify_fallow_land(year, input_dir, output_dir)
