# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 15:27:09 2024

@author: s224016798
"""

from osgeo import gdal, ogr

def clip_raster_with_shapefile(raster_path, shapefile_path, output_path):
    # 打开矢量数据
    shapefile = ogr.Open(shapefile_path)
    layer = shapefile.GetLayer()

    # 打开栅格数据
    raster = gdal.Open(raster_path)
    gdal.Warp(output_path, raster, format='GTiff', cutlineDSName=shapefile_path, cutlineLayer=layer.GetName(), cropToCutline=True)

# 使用函数
clip_raster_with_shapefile('F:/Jingyi/CLCD/Fallowland/fallow_land_test_1990-1991-1992.tif', 'F:/Jingyi/CLCD/Test/QJ_project.shp', 'F:/Jingyi/CLCD/Fallowland/fallow_land_test_1990-1991-1992_QJ.tif')
