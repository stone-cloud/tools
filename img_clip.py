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
          fliter: bool = False,
          percent: float = -1,
          percent_nodata: float = 0) -> np.ndarray:
    """

    """
    if fliter:
        assert (percent <= 1) and (percent >= 0), 'percent 必须在0-1之间'
    if percent_nodata:
        assert (percent_nodata <= 1) and (percent_nodata >= 0), 'percent_nodata 必须在0-1之间'
    rows = index[1] - index[0]
    cols = index[3] - index[2]
    if len(img_data.shape) > 2:
        if edge_fill:
            if fliter:
                if (rows != slice_size) or (cols != slice_size):
                    if ((rows * cols / (slice_size * slice_size)) >= percent):
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
            result = img_data[index[0]:index[1], index[2]:index[3], :]
    else:
        if edge_fill:
            if fliter:
                if (rows != slice_size) or (cols != slice_size):
                    if ((rows * cols / (slice_size * slice_size)) >= percent):
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
        else:
            result = img_data[index[0]:index[1], index[2]:index[3]]

    if len(result.shape) > 2:
        if np.nansum(result) >= (percent_nodata * slice_size * slice_size * result.shape[2]):
            return result.astype(img_data.dtype)
        else:
            return None
    else:
        if np.nansum(result) >= (percent_nodata * slice_size * slice_size):
            return result.astype(img_data.dtype)
        else:
            return None


if __name__ == '__main__':
    root = r'D:\LYH\dataset\greenhouse'
    out_root = r'D:\LYH\dataset\greenhouse\samples_512'
    save_8bit_dir = r'D:\LYH\dataset\water\0807\8bit'
    slice_size = 512
    transfor_8bit = False
    prefixs = ['images', 'labels']
    img_list = glob.glob(osp.join(root, prefixs[0]) + '/*.tif')
    label_root = osp.join(root, prefixs[1])
    # img_list = [r'D:\LYH\dataset\water\3612\GF1B_3612.tif']
    # print(f"共读取影像{len(img_list)}景，输出路径为{out_root}")
    # for img in img_list:
    #     img_data = mmcv.imread(img, backend='tifffile')
    #     # label_data = mmcv.imread(img.replace('tif', 'png'))
    #     label_data = Image.open(img.replace('.tif', '_label.tif'))
    #     label_data = np.asarray(label_data)
    #     print(label_data.shape)
    #     assert img_data.shape[0] == label_data.shape[0], '影像行数量与标注行数量不匹配'
    #     assert img_data.shape[1] == label_data.shape[1], '影像列数量与标注列数量不匹配'
    #     indexs = slice_index(img_data, slice_size=slice_size)
    #     percent = 0.2
    #     for i, idx in enumerate(indexs):
    #         img_slice_data = slice(img_data, idx, slice_size=slice_size, edge_fill=True, fliter=True, percent=percent)
    #         label_slice_data = slice(label_data, idx, slice_size=slice_size, edge_fill=True, fliter=True, percent=percent)
    #         if img_slice_data is not None:
    #             mmcv.imwrite(img_slice_data, osp.join(out_root, 'images', osp.basename(img).replace('.tif', '_' + str(i) + '.tif')))
    #         if label_slice_data is not None:
    #             # print(label_slice_data.shape)
    #             label_slice_data = Image.fromarray(np.uint8(label_slice_data > 0), mode='L')
    #             label_slice_data.save(osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.tif')))
    #             # mmcv.imwrite(label_slice_data,
    #             #              osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.png')))
    #         print(f"影像{img}已输出，输出路径为{osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.tif'))}")
    for i, img in enumerate(img_list):
        print(f"""第{i + 1}景影像开始处理，影像名：{os.path.basename(img)}""")
        save_8bit_path = img.replace(osp.join(root, prefixs[0]), save_8bit_dir)

        if transfor_8bit:
            save_8bit_path = save_8bit_path.replace(os.path.splitext(save_8bit_path)[-1], '_8bit.tif')
            print(f"""第{ i + 1}景影像开始转8位，影像名：{os.path.basename(img)}""")
            _, image_info = imageto8bit(img, save_8bit_path=save_8bit_path)
        # data_8bit = data_8bit.astype(np.uint8)
            img_data = mmcv.imread(save_8bit_path, backend='tifffile')
        else:
            img_data = mmcv.imread(img, backend='tifffile')
        label_data = mmcv.imread(osp.join(label_root, osp.basename(save_8bit_path).replace('.tif', '_label.tif')),
                                 backend='tifffile')
        assert img_data.shape[0] == label_data.shape[0], '影像行数量与标注行数量不匹配'
        assert img_data.shape[1] == label_data.shape[1], '影像列数量与标注列数量不匹配'
        indexs = slice_index(img_data, slice_size=slice_size)
        percent = 0.2
        percent_nodata = 0.3
        for i, idx in enumerate(indexs):
            label_slice_data = slice(label_data, idx, slice_size=slice_size, edge_fill=True, fliter=True,
                                     percent=percent, percent_nodata=percent_nodata)
            # print(np.unique(label_slice_data))
            if label_slice_data is not None:
                mmcv.imwrite(label_slice_data,
                             osp.join(out_root, 'labels', osp.basename(img).replace('.tif', '_' + str(i) + '.png')))
                img_slice_data = slice(img_data, idx, slice_size=slice_size, edge_fill=True, fliter=True,
                                       percent=percent, percent_nodata=percent_nodata)
            # print(np.unique(img_slice_data))
            # label_slice_data = slice(label_data, idx, slice_size=slice_size, edge_fill=True, fliter=True, percent=percent, percent_nodata=percent_nodata)
                if img_slice_data is not None:
                    mmcv.imwrite(img_slice_data, osp.join(out_root, 'images',
                                                          osp.basename(img).replace('.tif', '_' + str(i) + '.tif')))
            print(f"影像{img}已输出，输出路径为{osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.tif'))}")
