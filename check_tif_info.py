# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 20:10:01 2024

@author: s224016798
"""

from osgeo import gdal
import numpy as np

def read_raster_info(raster_file):
    # 打开栅格文件
    dataset = gdal.Open(raster_file)
    if not dataset:
        print("文件无法打开")
        return

    print(f"文件描述: {dataset.GetDescription()}")
    # 获取栅格的大小和波段数量
    nCols = dataset.RasterXSize
    nRows = dataset.RasterYSize
    nBands = dataset.RasterCount
    
    print(f"栅格尺寸: {nCols} x {nRows}")
    print(f"波段数量: {nBands}")
    
    # 遍历每个波段并打印基本信息及计算平均值
    for i in range(1, nBands + 1):
        band = dataset.GetRasterBand(i)
        bandType = gdal.GetDataTypeName(band.DataType)
        print(f"波段 {i} 类型: {bandType}")
        
        minVal, maxVal = band.ComputeRasterMinMax(True)
        print(f"波段 {i} 最小值: {minVal}, 最大值: {maxVal}")
        
        noDataValue = band.GetNoDataValue()
        if noDataValue is not None:
            print(f"波段 {i} 无数据值: {noDataValue}")
        
        # 读取波段数据为数组
        data = band.ReadAsArray()
        # 将无数据值替换为NaN，以便在计算平均值时忽略这些值
        if noDataValue is not None:
            data = np.where(data == noDataValue, np.nan, data)
        # 计算平均值
        avgVal = np.nanmean(data)
        print(f"波段 {i} 平均值: {avgVal}")

    dataset = None  # 关闭文件

if __name__ == "__main__":
    raster_file = r"F:\Jingyi\Climate\Dismo\output_1990_2022_WGS84_Albert\biovar_19_1990_WGS84.tif"  # 替换为你的栅格文件路径
    read_raster_info(raster_file)

