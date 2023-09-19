import mmcv
import os
import os.path as osp
import glob
import numpy as np
import math
from typing import List, Optional
from PIL import Image
from slice import *

def imageto8bit(image_path, save_8bit_path=None):
    image, image_info, _ = read_multi_bands(image_path)
    data_8bit = image.trans_img_16bit_to_8bit()
    if save_8bit_path:
        write_img(save_8bit_path, data_8bit.astype(np.uint8), img_geotrans=image_info[3], img_proj=image_info[4])
        print("8位影像保存完成")
    return data_8bit, image_info

def slice_index(img_data: np.ndarray,
                stride: Optional[int] = None,
                slice_size: int = 1024) -> List:

    if len(img_data.shape) == 3:
        single_band_size = img_data.shape[:2]
    else:
        single_band_size = img_data.shape
    row_num = math.ceil(single_band_size[0] / slice_size)  # 向上取整
    col_num = math.ceil(single_band_size[1] / slice_size)  # 向上取整
    print(f"行列数：{single_band_size}，行分割数量：{row_num}，列分割数量：{col_num}")
    slice_index = []
    for i in range(row_num):
        for j in range(col_num):
            row_min = i * slice_size
            row_max = (i + 1) * slice_size
            if (i + 1) * slice_size > single_band_size[0]:
                row_max = single_band_size[0]
            col_min = j * slice_size
            col_max = (j + 1) * slice_size
            if (j + 1) * slice_size > single_band_size[1]:
                col_max = single_band_size[1]
            slice_index.append([row_min, row_max, col_min, col_max])
    return slice_index

def slice(img_data: np.ndarray,
          index: List,
          slice_size: int = 1024,
          edge_fill: bool = False,
          percent_fill: float = 0,
          percent_nodata: float = 0) -> np.ndarray:

    if isinstance(percent_fill, float):
        assert (percent_fill <= 1) and (percent_fill >= 0), 'percent 必须在0-1之间'
    if percent_nodata:
        assert (percent_nodata <= 1) and (percent_nodata >= 0), 'percent_nodata 必须在0-1之间'
    rows = index[1] - index[0]
    cols = index[3] - index[2]
    if len(img_data.shape) > 2:
        if edge_fill and (rows != slice_size) or (cols != slice_size):
            if ((rows * cols / (slice_size * slice_size)) >= percent_fill):
                result = np.empty(shape=(slice_size, slice_size, img_data.shape[2]))
                new_row_min = index[0] % slice_size
                new_row_max = new_row_min + (index[1] - index[0])
                new_col_min = index[2] % slice_size
                new_col_max = new_col_min + (index[3] - index[2])
                result[new_row_min:new_row_max, new_col_min:new_col_max, :] = img_data[index[0]:index[1],
                                                                              index[2]:index[3], :]
            else:
                return None
        else:
            result = img_data[index[0]:index[1], index[2]:index[3], :]
    else:
        if edge_fill and (rows != slice_size) or (cols != slice_size):
            if ((rows * cols / (slice_size * slice_size)) >= percent_fill):
                result = np.empty(shape=(slice_size, slice_size))
                new_row_min = index[0] % slice_size
                new_row_max = new_row_min + (index[1] - index[0])
                new_col_min = index[2] % slice_size
                new_col_max = new_col_min + (index[3] - index[2])
                result[new_row_min:new_row_max, new_col_min:new_col_max] = img_data[index[0]:index[1],
                                                                              index[2]:index[3]]
            else:
                return None
        else:
            result = img_data[index[0]:index[1], index[2]:index[3]]

    if len(result.shape) > 2:
        if np.nansum(result > 0) >= (percent_nodata * slice_size * slice_size * result.shape[2]):
            return result.astype(img_data.dtype)
        else:
            return None
    else:
        if np.nansum(result > 0) >= (percent_nodata * slice_size * slice_size):
            return result.astype(img_data.dtype)
        else:
            return None


if __name__ == '__main__':
    root = r'D:\LYH\dataset\changeSB\First'
    out_root = r'D:\LYH\dataset\changeSB\512_First'
    save_8bit_dir = r'D:\LYH\dataset\water\0807\8bit'
    slice_size = 512
    transfor_8bit = False
    prefixs = ['images/A', 'images/B', 'labels']
    img_A_list = glob.glob(osp.join(root, prefixs[0]) + '/*.tif')
    label_root = osp.join(root, prefixs[2])

    for i, img_A in enumerate(img_A_list):
        print(f"""第{i + 1}景影像开始处理，影像名：{os.path.basename(img_A)}""")
        img_B = img_A.replace(prefixs[0], prefixs[1])
        save_A_8bit_path = img_A.replace(root, save_8bit_dir)
        save_B_8bit_path = img_B.replace(root, save_8bit_dir)

        if transfor_8bit:
            # save_A_8bit_path = save_A_8bit_path.replace(os.path.splitext(save_A_8bit_path)[-1], '_8bit.tif')
            # save_B_8bit_path = save_B_8bit_path.replace(os.path.splitext(save_B_8bit_path)[-1], '_8bit.tif')
            print(f"""第{ i + 1}景影像开始转8位，影像名：{os.path.basename(img_A)}""")
            _, image_A_info = imageto8bit(img_A, save_8bit_path=save_A_8bit_path)
            _, image_B_info = imageto8bit(img_B, save_8bit_path=save_B_8bit_path)
        # data_8bit = data_8bit.astype(np.uint8)
            img_A_data = mmcv.imread(save_A_8bit_path, backend='tifffile')
            img_B_data = mmcv.imread(save_B_8bit_path, backend='tifffile')
        else:
            img_A_data = mmcv.imread(img_A, backend='tifffile')
            img_B_data = mmcv.imread(img_B, backend='tifffile')
        print(osp.join(label_root, osp.basename(save_A_8bit_path)))
        label_data = mmcv.imread(osp.join(label_root, osp.basename(save_A_8bit_path)),
                                 backend='tifffile')
        assert img_A_data.shape == img_B_data.shape, '两时相行列数量不匹配'
        assert img_A_data.shape[0] == label_data.shape[0], '影像行数量与标注行数量不匹配'
        assert img_A_data.shape[1] == label_data.shape[1], '影像列数量与标注列数量不匹配'
        indexs = slice_index(img_A_data, slice_size=slice_size)
        percent = 0.2
        percent_nodata = 0.00001
        with alive_bar(len(indexs), force_tty=True) as bar:
            for i, idx in enumerate(indexs):
                label_slice_data = slice(label_data, idx, slice_size=slice_size, edge_fill=True,
                                         percent_fill=percent, percent_nodata=percent_nodata)
                # print(np.unique(label_slice_data))
                if label_slice_data is not None:
                    mmcv.imwrite(label_slice_data,
                                 osp.join(out_root, prefixs[2], osp.basename(img_A).replace('.tif', '_' + str(i) + '.png')))
                    img_A_slice_data = slice(img_A_data, idx, slice_size=slice_size, edge_fill=True,
                                           percent_fill=percent, percent_nodata=percent_nodata)
                    img_B_slice_data = slice(img_B_data, idx, slice_size=slice_size, edge_fill=True,
                                           percent_fill=percent, percent_nodata=percent_nodata)
                # print(np.unique(img_slice_data))
                    if img_A_slice_data is not None:
                        mmcv.imwrite(img_A_slice_data, osp.join(out_root, prefixs[0],
                                                              osp.basename(img_A).replace('.tif', '_' + str(i) + '.tif')))
                        mmcv.imwrite(img_B_slice_data, osp.join(out_root, prefixs[1],
                                                                osp.basename(img_A).replace('.tif', '_' + str(i) + '.tif')))
                bar()
        print(f"影像{img_A}已输出，输出路径为{osp.join(out_root)}")
