import rasterio
import numpy as np
import os
import pandas as pd
from tqdm import tqdm  # 引入tqdm库

# 地类数据的固定路径
path_to_data_A = 'N:/ChinaROI/CTAMAP/Python/China_City_2020_Raster_1000m.tif'

# 打开地类栅格数据文件
with rasterio.open(path_to_data_A) as src_A:
    data_A = src_A.read(1)  # 读取第一个波段
    profile_A = src_A.profile

    # 将特定值设置为0
    data_A[data_A == 65535] = 0

# 确定地类数据中的最大地类编号
max_label = np.max(data_A)

# 定义降水数据文件夹路径
folder_path = 'N:/Climate/Dismo/output_1990_2022_test'

# 读取一幅降水量数据来确定栅格大小和数据类型
with rasterio.open(os.path.join(folder_path, next(f for f in os.listdir(folder_path) if f.endswith('.tif')))) as sample_src:
    sample_data = sample_src.read(1)

# 创建一个与sample_data尺寸相同的空白栅格data_A_resized，初始化为0，数据类型为整型
data_A_resized = np.zeros(sample_data.shape, dtype=int)
data_A_resized[:data_A.shape[0], :data_A.shape[1]] = np.nan_to_num(data_A, nan=0).astype(int)

# 初始化字典来存储每个文件的数据
results_counts = {}
results_sums = {}
results_averages = {}

# 遍历文件夹中的所有降水数据文件
tif_files = [f for f in os.listdir(folder_path) if f.endswith('.tif')]
for filename in tqdm(tif_files, desc="Processing files"):  # 使用tqdm来添加进度条
    path_to_data_B = os.path.join(folder_path, filename)  # 降水数据的路径

    # 读取降水量数据
    with rasterio.open(path_to_data_B) as src_B:
        data_B = src_B.read(1)  # 假设降水数据在第一个波段
        mask = data_B >= -1000  # 创建遮罩

        # 更新总降水量和地类计数
        valid_data_A_resized = data_A_resized[mask]
        valid_data_B = data_B[mask]
        local_sum = np.bincount(valid_data_A_resized, weights=valid_data_B, minlength=max_label+1)
        local_count = np.bincount(valid_data_A_resized, minlength=max_label+1)
        local_average = np.where(local_count > 0, local_sum / local_count, np.nan)

        # 存储每个文件的数据
        results_sums[os.path.splitext(filename)[0]] = local_sum[1:]
        results_counts[os.path.splitext(filename)[0]] = local_count[1:]
        results_averages[os.path.splitext(filename)[0]] = local_average[1:]

# 准备数据并保存为Excel，每个文件名对应一列
df_counts = pd.DataFrame(results_counts, index=range(1, max_label+1))
df_sums = pd.DataFrame(results_sums, index=range(1, max_label+1))
df_averages = pd.DataFrame(results_averages, index=range(1, max_label+1))

# 使用ExcelWriter将多个DataFrame写入同一个Excel文件的不同Sheet中
with pd.ExcelWriter("N:/Climate/Dismo/output_1990_2022_test/China_dismo_1990_2022.xlsx") as writer:
    df_counts.to_excel(writer, sheet_name='Counts')
    df_sums.to_excel(writer, sheet_name='Sums')
    df_averages.to_excel(writer, sheet_name='Averages')

