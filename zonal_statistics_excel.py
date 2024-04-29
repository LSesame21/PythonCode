# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 10:18:23 2024

@author: s224016798
"""

from osgeo import gdal, ogr, osr
import geopandas as gpd
import pandas as pd
import numpy as np
import glob

def get_raster_stats(raster_path, geom):
    src_raster = gdal.Open(raster_path)
    if not src_raster:
        raise IOError("Could not open raster file: " + raster_path)

    src_band = src_raster.GetRasterBand(1)
    no_data_value = src_band.GetNoDataValue()  # 获取无数据值

    # 获取栅格的空间参考
    srs = osr.SpatialReference(wkt=src_raster.GetProjection())

    # 创建一个临时内存数据集
    mem_driver = gdal.GetDriverByName('MEM')
    mem_ds = mem_driver.Create('', src_band.XSize, src_band.YSize, 1, gdal.GDT_Float32)
    mem_ds.SetProjection(src_raster.GetProjection())
    mem_ds.SetGeoTransform(src_raster.GetGeoTransform())
    mem_band = mem_ds.GetRasterBand(1)
    mem_band.Fill(np.nan)  # 使用NaN初始化内存数据集

    # 创建一个临时矢量图层进行栅格化，使用相同的空间参考
    mem_vector_ds = ogr.GetDriverByName('Memory').CreateDataSource('memData')
    mem_layer = mem_vector_ds.CreateLayer('memLayer', geom_type=ogr.wkbPolygon, srs=srs)
    feature_def = mem_layer.GetLayerDefn()
    feature = ogr.Feature(feature_def)
    feature.SetGeometry(ogr.CreateGeometryFromWkt(geom.wkt))
    mem_layer.CreateFeature(feature)
    
    # 栅格化内存中的矢量图层
    gdal.RasterizeLayer(mem_ds, [1], mem_layer, burn_values=[1])

    # 应用掩码选择覆盖区域
    mask = mem_band.ReadAsArray()
    data = src_band.ReadAsArray()

    # 将小于-3267或无数据值的数据点设为NaN
    data = np.where((data < -3267) | (data == no_data_value), np.nan, data)

    # 仅包含感兴趣区域的数据
    masked_data = np.ma.masked_array(data, mask != 1)
    masked_data = masked_data[~np.isnan(masked_data)]

    # 计算平均值，忽略NaN值
    mean_val = np.ma.mean(masked_data)

    # 如果结果被掩码（所有值都是NaN），返回NaN
    return mean_val if not np.ma.is_masked(mean_val) else np.nan

# 文件路径
vector_path = r'F:\Jingyi\ChinaROI\CTAMAP\Python\China_City_2020_Del_Albert_Project.shp'
raster_folder = r'F:\Jingyi\Climate\Dismo\output_1990_2022_WGS84_Albert\\'
raster_paths = glob.glob(raster_folder + '*.tif')

# 读取矢量数据
gdf = gpd.read_file(vector_path)

# 初始化一个DataFrame存储结果
results_df = pd.DataFrame()

for raster_path in raster_paths:
    filename = raster_path.split('\\')[-1]
    core_name = '_'.join(filename.split('_')[:-1])
    mean_values = []
    for geom in gdf.geometry:
        mean_val = get_raster_stats(raster_path, geom)
        mean_values.append(mean_val)
    results_df[core_name] = mean_values

# 合并矢量数据名称或其他标识符
results_df['ENG_NAME'] = gdf['ENG_NAME']

# 输出到Excel文件
output_path = r'F:\Jingyi\Climate\Dismo\Biovar_1990_2022_China.xlsx'
results_df.to_excel(output_path, index=False)
