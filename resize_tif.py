# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 14:01:32 2024

@author: s224016798
"""

import sys
import numpy as np
from osgeo import gdal
import glob
import os

def ReadRaster(rasterFile):
    ds = gdal.Open(rasterFile)
    nCols = ds.RasterXSize
    nRows = ds.RasterYSize
    geotrans = ds.GetGeoTransform()
    srs = ds.GetProjection()
    bandCount = ds.RasterCount  # 获取波段数
    data = np.zeros((bandCount, nRows, nCols))  # 根据波段数创建一个三维数组
    noDataValue = None
    
    for i in range(bandCount):
        band = ds.GetRasterBand(i + 1)  # GDAL中波段计数是从1开始的
        data[i, :, :] = band.ReadAsArray()
        if noDataValue is None:  # 假设所有波段的NoDataValue相同
            noDataValue = band.GetNoDataValue()

    return {'data': data, 'nCols': nCols, 'nRows': nRows, 'geotrans': geotrans, 'srs': srs, 'noDataValue': noDataValue}


def WriteGTiffFile(outputFile, data, geotrans, srs, noDataValue, dataType=gdal.GDT_Float32):
    # 确定波段数、行数和列数
    bandCount, nRows, nCols = data.shape

    # 创建输出文件
    driver = gdal.GetDriverByName('GTiff')
    outDs = driver.Create(outputFile, nCols, nRows, bandCount, dataType)
    outDs.SetGeoTransform(geotrans)  # 设置地理变换
    outDs.SetProjection(srs)  # 设置空间参考

    # 遍历所有波段，写入数据
    for i in range(bandCount):
        outBand = outDs.GetRasterBand(i + 1)
        outBand.WriteArray(data[i, :, :])  # 写入当前波段的数据
        outBand.SetNoDataValue(noDataValue)  # 设置无数据值
        outBand.FlushCache()

    outDs = None  # 关闭文件，确保内容写入硬盘


def DataMacth(in_base_raster, in_mtc_raster, out_raster, rc=[0, 0, 0, 0]):
    # 读取基准栅格数据与待匹配栅格数据及其属性参数
    r_in_mtc = ReadRaster(in_mtc_raster)
    r_in_base = ReadRaster(in_base_raster)
    mtcdata = r_in_mtc['data']  # 使用字典键来访问
    nCols = r_in_base['nCols']  # 使用字典键来访问
    nRows = r_in_base['nRows']  # 使用字典键来访问
    geoTrans = r_in_base['geotrans']  # 使用字典键来访问
    srs = r_in_base['srs']  # 使用字典键来访问
    NDV = r_in_mtc['noDataValue']  # 使用字典键来访问
    
    data_new = np.full((r_in_base['data'].shape[0], nRows, nCols), NDV) # 使用NDV初始化新数据
    # 计算裁剪或填充边界
    up, down, left, right = max(0, rc[0]), max(0, rc[1]), max(0, rc[2]), max(0, rc[3])
    
    for b in range(r_in_base['data'].shape[0]):  # 遍历所有波段
        # 确定目标区域
        target_rows = slice(up, nRows - down)
        target_cols = slice(left, nCols - right)
        # 确定源区域
        source_rows = slice(0, nRows - up - down)
        source_cols = slice(0, nCols - left - right)
        
        # 在目标区域内复制数据
        data_new[b, target_rows, target_cols] = mtcdata[b, source_rows, source_cols]
                    
    # 输出栅格数据
    WriteGTiffFile(out_raster, data_new, geoTrans, srs, NDV, gdal.GDT_Float32)

    print("\tSave as: %s" % out_raster)
    
def ProcessFolder(in_base_raster, in_mtc_raster_folder, out_raster_folder, rc=[0, 0, 0, 0]):
    '''
    :param in_base_raster: 基准栅格数据文件路径
    :param in_mtc_raster_folder: 待匹配栅格数据文件夹路径
    :param out_raster_folder: 输出栅格数据文件夹路径
    :param rc: <up, down, left, right>
    :return:
    '''
    # 确保输出文件夹存在
    if not os.path.exists(out_raster_folder):
        os.makedirs(out_raster_folder)

    # 获取文件夹中所有.tif文件
    mtc_raster_files = glob.glob(os.path.join(in_mtc_raster_folder, "*.tif"))
    
    for in_mtc_raster in mtc_raster_files:
        # 构造输出栅格数据的文件名
        out_raster = os.path.join(out_raster_folder, os.path.basename(in_mtc_raster))
        
        # 对每个待匹配的栅格数据文件进行处理
        DataMacth(in_base_raster, in_mtc_raster, out_raster, rc)

if __name__ == "__main__":
    in_base_raster = "F:/Jingyi/Climate/ChinaDataset/monthly_data/prelzw_1970_2000/pre_1970.tif"
    in_mtc_raster_folder = "F:/Jingyi/Climate/WorldClim/Future/China/monthly_data/tmx/"
    out_raster_folder = "F:/Jingyi/Climate/WorldClim/Future/China/monthly_data/tmx_resize/"
    rc = [-1, 0, -1, 0]  # 根据需要调整
    ProcessFolder(in_base_raster, in_mtc_raster_folder, out_raster_folder, rc)

