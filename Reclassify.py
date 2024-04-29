# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from osgeo import gdal
import numpy as np
from tqdm import tqdm

def reclassify_block(block):
    """重分类数据块"""
    reclassified_block = np.where(np.isin(block, [2, 3, 4, 7]), 0, block)
    reclassified_block = np.where(np.isin(reclassified_block, [5, 6, 8, 9]), 2, reclassified_block)
    return reclassified_block

def process_raster(input_path, output_path, block_size=1024):
    """分块处理单个遥感影像并使用tqdm显示进度"""
    dataset = gdal.Open(input_path)
    band = dataset.GetRasterBand(1)

    driver = gdal.GetDriverByName('GTiff')
    options = ['COMPRESS=LZW']  # 使用LZW压缩
    out_dataset = driver.Create(output_path, dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_Byte, options=options)
    out_band = out_dataset.GetRasterBand(1)

    out_dataset.SetGeoTransform(dataset.GetGeoTransform())
    out_dataset.SetProjection(dataset.GetProjection())

    total_blocks = ((band.XSize - 1) // block_size + 1) * ((band.YSize - 1) // block_size + 1)

    with tqdm(total=total_blocks, desc=f"Processing {input_path}") as pbar:
        for x in range(0, band.XSize, block_size):
            for y in range(0, band.YSize, block_size):
                w = min(block_size, band.XSize - x)
                h = min(block_size, band.YSize - y)
                block = band.ReadAsArray(x, y, w, h)
                block = reclassify_block(block)
                out_band.WriteArray(block, x, y)
                pbar.update(1)

    out_band.FlushCache()
    out_dataset = None
    dataset = None

def process_all_years(start_year, end_year, input_dir, output_dir, file_pattern="CLCD_v01_{year}_albert.tif", block_size=1024):
    """处理一系列年份的遥感影像数据"""
    years = range(start_year, end_year + 1)
    for year in tqdm(years, desc="Overall Progress"):
        input_path = f"{input_dir}/{file_pattern.format(year=year)}"
        output_path = f"{output_dir}/CLCD_Reclassified_{year}.tif"
        process_raster(input_path, output_path, block_size)

# 示例：处理从1990到2022年的遥感影像
input_dir = 'F:/Jingyi/CLCD/OriginalData'
output_dir = 'F:/Jingyi/CLCD/Reclassify1'
process_all_years(2016, 2022, input_dir, output_dir)
