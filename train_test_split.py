import random
import os.path as osp
import os
import shutil
from mmengine import mkdir_or_exist

data_root = r'D:\LYH\dataset\SECOND_train_set'
out_root = r'D:\LYH\dataset\SECOND_train_test'
mkdir_or_exist(out_root)
prefixs = ['im1', 'im2', 'label', 'label1', 'label2']
backend = ['.png', '.png', '.png', '.png', '.png']
data_list = os.listdir(osp.join(data_root, prefixs[0]))
random.shuffle(data_list)
train_list = data_list[:int(len(data_list)*0.85)]
test_list = data_list[int(len(data_list)*0.85): ]

for img in train_list:
    for prefix, bk in zip(prefixs, backend):
        img_name = osp.splitext(img)[0] + bk
        img_path = osp.join(data_root, prefix, img_name)
        img_out_path = osp.join(out_root, 'train', prefix)
        mkdir_or_exist(img_out_path)
        shutil.move(img_path, osp.join(img_out_path, img_name))
        # img_path = osp.join(data_root, prefixs[1], img)
        # img_out_path = osp.join(out_root, 'train/B')
        # mkdir_or_exist(img_out_path)
        # shutil.move(img_path, osp.join(img_out_path, img))
        # label_path = osp.join(data_root, prefixs[2], img.replace('.tif', '.png'))
        # label_out_path = osp.join(out_root, 'train/labels')
        # mkdir_or_exist(label_out_path)
        # shutil.move(label_path, osp.join(label_out_path, img))
for img in test_list:
    for prefix, bk in zip(prefixs, backend):
        img_name = osp.splitext(img)[0] + bk
        img_path = osp.join(data_root, prefix, img_name)
        img_out_path = osp.join(out_root, 'val', prefix)
        mkdir_or_exist(img_out_path)
        shutil.move(img_path, osp.join(img_out_path, img_name))
    # img_path = osp.join(data_root, prefixs[1], img)
    # img_out_path = osp.join(out_root, 'val/B')
    # mkdir_or_exist(img_out_path)
    # shutil.move(img_path, osp.join(img_out_path, img))
    # label_path = osp.join(data_root, prefixs[2], img.replace('.tif', '.png'))
    # label_out_path = osp.join(out_root, 'val/labels')
    # mkdir_or_exist(label_out_path)
    # shutil.move(label_path, osp.join(label_out_path, img))