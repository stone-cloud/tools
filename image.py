from osgeo import gdal
import numpy as np
import os
os.environ['PROJ_LIB'] = r'C:\Users\Lenovo\.conda\envs\zph\Library\share\proj'
os.environ['GDAL_DATA'] = r'C:\Users\Lenovo\.conda\envs\zph\Library\share'
gdal.PushErrorHandler("CPLQuietErrorHandler")


class ImageProcess:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dataset = gdal.Open(self.filepath, gdal.GA_ReadOnly)
        self.info = []
        self.img_data = None
        self.data_8bit = None
        self.img_nodata = self.dataset.GetRasterBand(1).GetNoDataValue()

    def read_img_info(self):
        # 获取波段、宽、高
        img_bands = self.dataset.RasterCount
        img_width = self.dataset.RasterXSize
        img_height = self.dataset.RasterYSize
        # 获取仿射矩阵、投影
        img_geotrans = self.dataset.GetGeoTransform()
        img_proj = self.dataset.GetProjection()
        self.info = [img_bands, img_width, img_height, img_geotrans, img_proj]
        return self.info

    def read_img_data(self):
        self.img_data = self.dataset.ReadAsArray(0, 0, self.info[1], self.info[2])
        return self.img_data



    # @jit
    def trans_img_16bit_to_8bit(self, low_per_raw=0.01, high_per_raw=0.99):
        # array_data = self.img_data
        # print(self.info[0])
        # print(self.info[1])
        # print(self.info[2])
        bands, cols, rows = self.info[0:3]  # array_data, (4, 36786, 37239) ,波段，行，列
        # print("1读取数组形状", self.img_data.shape)
        # 这里控制要输出的是几位
        self.data_8bit = np.zeros((bands, rows, cols), dtype=np.uint8)
        self.img_data[self.img_data == self.img_nodata] = 0
        # self.img_data[self.img_data < 0] = 0

        for i in range(bands):
            # 得到百分比对应的值，得到0代表的黑边的占比
            cnt_array = np.where(self.img_data[i, :, :], 0, 1)
            num0 = np.sum(cnt_array)
            # nodata_array = np.where(array_data[i, :, :] == 32767, 1, 0)
            # num1 = np.sum(nodata_array)
            kk = (num0) / (rows * cols)  # 得到0的比例
            # kk1 = (num1) / (rows * cols)  # 得到nodata的比例

            # 这里是去掉黑边0值，否则和arcgis的不一样，这样也有偏差，只算剩下的百分比
            low_per = low_per_raw + kk - low_per_raw * kk  # (A*x-A*KK)/(A-A*KK)=0.01, X = 0.99KK+0.01
            # low_per = low_per_raw + kk
            low_per = low_per * 100
            high_per = (1 - high_per_raw) * (1 - kk)  # A*x/(A-A*KK) = 0.04, X =  0.04-(0.04*kk)
            high_per = 100 - high_per * 100
            # high_per = kk1
            # high_per = high_per_raw *(100 - high_per * 100)
            print("baifen:", low_per, high_per)

            cutmin = np.percentile(self.img_data[i, :, :], low_per)
            cutmax = np.percentile(self.img_data[i, :, :], high_per)
            print("duandian:", cutmin, cutmax)

            data_band = self.img_data[i]
            # 进行截断
            data_band[data_band < cutmin] = cutmin
            data_band[data_band > cutmax] = cutmax
            # 进行缩放
            self.data_8bit[i, :, :] = np.around((data_band[:, :] - cutmin) * 255 / (cutmax - cutmin))

        print("最大最小值：", np.max(self.data_8bit), np.min(self.data_8bit))
        return self.data_8bit.astype(np.uint8)

# 影像写入文件
def write_img(filename: str, img_data: np.array, **kwargs):
    # 判断栅格数据的数据类型
    if 'int8' in img_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in img_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    # 判读数组维数
    if len(img_data.shape) >= 3:
        img_bands, img_height, img_width = img_data.shape
    else:
        img_bands, (img_height, img_width) = 1, img_data.shape
    # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    outdataset = driver.Create(filename, img_width, img_height, img_bands, datatype, options=['BigTIFF=YES', 'TILED=YES', 'COMPRESS=LZW'])
    # 写入仿射变换参数
    if 'img_geotrans' in kwargs:
        outdataset.SetGeoTransform(kwargs['img_geotrans'])
    # 写入投影
    if 'img_proj' in kwargs:
        outdataset.SetProjection(kwargs['img_proj'])
    # 写入文件
    if img_bands == 1:
        outdataset.GetRasterBand(1).WriteArray(img_data)  # 写入数组数据
    else:
        for i in range(img_bands):
            outdataset.GetRasterBand(i + 1).WriteArray(img_data[i])

    del outdataset

def read_multi_bands(image_path):
    """
    读取多波段文件
    :param image_path: 多波段文件路径
    :return: 影像对象，影像元信息，影像矩阵
    """
    # 影像读取
    image = ImageProcess(filepath=image_path)
    # 读取影像元信息
    image_info = image.read_img_info()
    print(f"多波段影像元信息：{image_info}")
    # 读取影像矩阵
    image_data = image.read_img_data()
    print(f"多波段矩阵大小：{image_data.shape}")
    return image, image_info, image_data


def read_single_band(band_path):
    """
    读取单波段文件
    :param band_path: 单波段文件路径
    :return: 影像对象，影像元信息，影像矩阵
    """
    # 影像读取
    band = ImageProcess(filepath=band_path)
    # 读取影像元信息
    band_info = band.read_img_info()
    print(f"单波段影像元信息：{band_info}")
    # 读取影像矩阵
    band_data = band.read_img_data()
    print(f"单波段矩阵大小：{band_data.shape}")
    return band, band_info, band_data
