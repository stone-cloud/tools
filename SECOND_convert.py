import numpy as np
import cv2
import os.path as osp
import os
from PIL import Image
from mmengine import mkdir_or_exist

dataroot = r'D:\LYH\dataset\SECOND_train_set'
labels = 'label1'
out_root = r'D:\LYH\dataset\SECOND_train_set\label1_w'
mkdir_or_exist(out_root)
train_data = osp.join(dataroot, labels)
# out_data = osp.join(out_root, labels)

classes = [[255, 255, 255], [0, 128, 0], [128, 128, 128],
           [0, 255, 0], [255, 0, 0], [0, 0, 128], [0, 0, 255]]
classes_name = ('unchanged', 'low vegetation', 'ground surface',
                'tree', 'water', 'building', 'playground')

for file in os.listdir(train_data):
    print(file)
    dataset = cv2.imread(osp.join(train_data, file.strip()))  # dataset.shape(w,h,c)(column, row, channel)
    # class_num = np.unique(dataset)
    class_data = np.zeros(dataset.shape[:2]).astype(np.uint8)
    for c in range(dataset.shape[0]):
        for r in range(dataset.shape[1]):
            # print(type(dataset[c][r].tolist()))
            # print(classes.index(dataset[c][r].tolist()))
            # print(class_data[c][r])
            class_data[c][r] = classes.index(dataset[c][r].tolist())
    class_num = np.unique(class_data)
    cv2.imwrite(osp.join(out_root, file.strip()), class_data)
    print(class_num)