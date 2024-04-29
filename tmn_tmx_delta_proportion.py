# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 14:27:35 2024

@author: s224016798
"""

import numpy as np
from osgeo import gdal
import glob
import os

def subtract_rasters(raster1_folder, raster2, output_folder):
    # 获取raster1_folder下所有的.tif文件
    raster1_files = glob.glob(os.path.join(raster1_folder, "*.tif"))
    
    # 打开第二幅栅格数据
    ds2 = gdal.Open(raster2)
    if ds2 is None:
        print("无法打开栅格数据文件: ", raster2)
        return
    
    for raster1 in raster1_files:
        ds1 = gdal.Open(raster1)
        if ds1 is None:
            print("无法打开栅格数据文件: ", raster1)
            continue
        
        # 获取栅格的基本信息
        nCols = ds1.RasterXSize
        nRows = ds1.RasterYSize
        geotrans = ds1.GetGeoTransform()
        srs = ds1.GetProjection()
        bandCount = ds1.RasterCount

        # 创建输出文件，文件名为raster1名称后面加_delta1
        output_raster = os.path.join(output_folder, os.path.basename(raster1).replace(".tif", "_delta.tif"))
        driver = gdal.GetDriverByName('GTiff')
        # 使用gdal.GDT_Float32确保输出数据类型为float32
        outDs = driver.Create(output_raster, nCols, nRows, bandCount, gdal.GDT_Float32)
        outDs.SetGeoTransform(geotrans)
        outDs.SetProjection(srs)

        # 对每个波段进行相减操作
        for i in range(1, bandCount + 1):
            band1 = ds1.GetRasterBand(i).ReadAsArray().astype(np.float32)  # 确保数据为float32
            band2 = ds2.GetRasterBand(i).ReadAsArray().astype(np.float32)
            result_band = band1 - band2
            
            # 将结果写入新的栅格文件
            outBand = outDs.GetRasterBand(i)
            outBand.WriteArray(result_band)
            outBand.FlushCache()

        # 清理
        ds1 = None
        outDs = None
    
    # 清理
    ds2 = None

# 示例调用
raster1_folder = r'F:\Jingyi\Climate\WorldClim\Future\China\monthly_data\pre'
raster2 = r'F:\Jingyi\Climate\WorldClim\Past\China\resize\wc2.1_30s_prec_merged_China_resize.tif'
output_folder = r'F:\Jingyi\Climate\Prediction\worldclim_delta\pre_test'
subtract_rasters(raster1_folder, raster2, output_folder)