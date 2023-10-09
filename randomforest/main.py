from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os
from untils import shp2ras, ras2shp
import os.path as osp
from image import read_multi_bands, read_single_band, write_img
import numpy as np
import warnings
warnings.simplefilter('ignore', np.RankWarning)
from joblib import dump, load
from pathlib import Path
import scipy.ndimage as nd

def Non_zero(x, y):
    ind = np.where(y != 0)
    ins = ind[0]
    x = x[ins, :]
    y = y[ins]
    return x, y, ins

def train_superviesd_methods(raster_root: Path,
                       label_root: Path,
                       temp_root: Path,
                       model_path: Path):
    if label_root.endswith('.shp'):
        label_ras = osp.join(temp_root, os.path.basename(label_root)[:-4] + '.tif')
        shp2ras(label_root, label_ras, field='value', snap_raster=raster_root)
    else:
        label_ras = label_root

    _, classes_ras_info, classes_ras_array = read_multi_bands(raster_root)
    _, label_ras_info, label_ras_array = read_single_band(label_ras)
    classes_ras_array = np.transpose(classes_ras_array, (1, 2, 0))
    assert classes_ras_array.shape[0] == label_ras_array.shape[0], '矢量和影像行数不一致'
    assert classes_ras_array.shape[1] == label_ras_array.shape[1], '矢量和影像列数不一致'
    # assert isinstance(classes_ras_array, np.ndarray), 'cuowu'
    # print(classes_ras_array.shape[0])
    classes_ras_data = classes_ras_array.reshape(-1, classes_ras_array.shape[2]) # 展成一行
    label_ras_data = label_ras_array.flatten()
    # class_ras_data_non, label_ras_data_non, _ = Non_zero(classes_ras_data, label_ras_data)

    scaler = StandardScaler().fit(classes_ras_data)
    classes_ras_data_s = scaler.transform(classes_ras_data)
    x_train, x_test, y_train, y_test = train_test_split(
        classes_ras_data_s, label_ras_data, test_size=0.3, random_state=42)

    # 构建随机森林模型
    RF = RandomForestClassifier(n_estimators=50, n_jobs=10)
    RF.fit(classes_ras_data_s, label_ras_data)

    model = dump(RF, model_path)
    return model

def predict_RF(raster_root,
               predict_root,
               model_path: Path,
               erosion: bool=True,
               component_size: int=50):
    _, ras_info, ras_array = read_multi_bands(raster_root)
    ras_array = np.transpose(ras_array, (1, 2, 0))
    r, c, b = ras_array.shape
    ras_data = ras_array.reshape(-1, b)
    ras_transform_data = StandardScaler().fit_transform(ras_data)
    model = load(model_path)
    # predict_data = np.zeros((r, c))
    predict_data = model.predict(ras_transform_data)
    predict_data = predict_data.reshape(r, c)
    if erosion:
        kernel = np.ones((2, 2))
        result_erosion = nd.binary_erosion(predict_data, structure=kernel)
        labels = nd.label(result_erosion, output=np.uint32)[0]
        unique, counts = np.unique(labels, return_counts=True)
        for (k, v) in dict(zip(unique, counts)).items():
            if v < component_size:
                result_erosion[labels == k] = 0
        final_result = nd.binary_dilation(result_erosion, structure=kernel).astype(np.uint8)
    else:
        final_result = predict_data
    write_img(predict_root, final_result, img_geotrans=ras_info[3], img_proj=ras_info[4])

if __name__ == '__main__':
    raster_root = r"D:\LYH\dataset\test_data\raw\GF1B_5365_1.tif"
    label_root = r"D:\LYH\dataset\test_data\label\GF1B_5365_label_Clip.shp"
    temp_root = r'D:\LYH\dataset\test_data\temp'
    model_path = r'D:\LYH\dataset\test_data\temp\model.joblib'
    predict_path = r'D:\LYH\dataset\test_data\predict\test.tif'
    component_size = 50
    # train_superviesd_methods(raster_root, label_root, temp_root, model_path)  # 训练模型
    predict_RF(raster_root, predict_path, model_path, True, component_size)