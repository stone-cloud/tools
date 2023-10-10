# 根据属性名称将矢量中的图层保存为单独的矢量文件，然后批量裁剪

from untils.clipTiffwithShp_mask import batch_clip_with_mask
from untils.feture2shp import featue_to_shp

# 拆分矢量
shp_path = r"D:\LYH\dataset\test\shp\F1.shp"  # 矢量文件路径，包含矢量名称
feature_path = r'D:\LYH\dataset\test\shp'  # 拆分后矢量保存路径，不需要文件名称
name_field = 'category'  # 拆分矢量的包含文件名的字段名
featue_to_shp(shp_path, feature_path, name_field)
raster_path = r'D:\LYH\dataset\test\tif'  # 栅格路径，不需要文件名
clip_out_path = r'D:\LYH\dataset\test\clip'  # 裁剪后保存的路径。裁剪后的文件名为矢量裁剪矢量名+被裁剪栅格名
batch_clip_with_mask(feature_path, raster_path, clip_out_path)