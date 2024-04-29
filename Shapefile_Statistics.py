# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 16:40:57 2024

@author: s224016798
"""
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import pandas as pd
import numpy as np

def calculate_area_of_class_per_vector_unit(vector_path, raster_path, class_value=11, pixel_area=900):
    # 读取矢量文件
    vector_data = gpd.read_file(vector_path)
    
    # 打开栅格文件并获取其CRS
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs
        # 确保矢量数据的CRS与栅格数据的CRS相匹配
        if vector_data.crs != raster_crs:
            vector_data = vector_data.to_crs(raster_crs)
        
        areas = []
        for index, vector_unit in vector_data.iterrows():
            vector_shape = [vector_unit['geometry']]
            out_image, out_transform = mask(src, vector_shape, crop=True, filled=True, nodata=src.nodata)
            out_image = out_image[0]
            
            # 检查裁剪后的栅格数据是否完全由NoData值组成
            if np.all(out_image == src.nodata):
                area = 0
            else:
                # 计算指定像素值的数量
                count = (out_image == class_value).sum()
                area = count * pixel_area 
            
            areas.append({'Vector_Unit': vector_unit.get('ENG_NAME'),'Area': area})
    
    areas_df = pd.DataFrame(areas)
    return areas_df

# 使用示例

vector_path = 'H:/Jingyi/ChinaROI/CTAMAP/Python/China_City_2020_Del.shp'  # 替换为你的矢量文件路径
raster_path = 'F:/Jingyi/CLCD/Fallowland1/fallow_land_test_2007-2008-2009.tif'  # 替换为你的栅格数据文件路径
areas_df = calculate_area_of_class_per_vector_unit(vector_path, raster_path)

# 保存为Excel文件

excel_path = 'H:/Jingyi/CroplandAbandon/fallow_land_test_2007-2008-2009.xlsx'  # 替换为你希望保存Excel文件的路径
areas_df.to_excel(excel_path, index=False, engine='openpyxl')

print(f"Results saved to {excel_path}")
