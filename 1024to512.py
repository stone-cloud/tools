import mmcv
import os.path as osp
from PIL import Image
import numpy as np
import glob
import os
from img_clip import slice, slice_index

if __name__ == '__main__':
    data_root = r'D:\LYH\dataset\greenhouse\greenhouse\images'
    label_root = r'D:\LYH\dataset\greenhouse\greenhouse\label'
    out_root = r'D:\LYH\dataset\greenhouse\greenhouse_512'
    img_list = glob.glob(data_root + '/*.tif')
    print(f"共读取影像{len(img_list)}景，输出路径为{out_root}")
    for img in img_list:
        img_data = mmcv.imread(img, backend='tifffile')
        # label_data = mmcv.imread(img.replace('tif', 'png'))
        label_data = Image.open(osp.join(label_root, os.path.basename(img).replace('tif', 'png')))
        label_data = np.asarray(label_data)
        # print(label_data.shape)
        assert img_data.shape[0] == label_data.shape[0], '影像行数量与标注行数量不匹配'
        assert img_data.shape[1] == label_data.shape[1], '影像列数量与标注列数量不匹配'
        indexs = slice_index(img_data, slice_size=512)
        percent = 0.2
        for i, idx in enumerate(indexs):
            img_slice_data = slice(img_data, idx, slice_size=512, edge_fill=True, fliter=True, percent=percent)
            label_slice_data = slice(label_data, idx, slice_size=512, edge_fill=True, fliter=True, percent=percent)
            if img_slice_data is not None:
                mmcv.imwrite(img_slice_data, osp.join(out_root, 'images', osp.basename(img).replace('.tif', '_' + str(i) + '.tif')))
            if label_slice_data is not None:
                # print(label_slice_data.shape)
                label_slice_data = Image.fromarray(np.uint8(label_slice_data > 0), mode='L')
                label_slice_data.save(osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.png')))
                # mmcv.imwrite(label_slice_data,
                #              osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.png')))
            print(f"影像{img}已输出，输出路径为{osp.join(out_root, 'label', osp.basename(img).replace('.tif', '_' + str(i) + '.png'))}")
