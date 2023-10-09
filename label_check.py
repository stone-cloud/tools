import numpy as np
import cv2
import os.path as osp
import os
from PIL import Image

dataroot = r'D:\LYH\dataset\SECOND_train_test\train'
imgs = "src"
labels = 'label1'

train_data = osp.join(dataroot, labels)
# with open(osp.join(dataroot, 'split/val.txt'), 'r+') as f:
#     line = [l for l in f.readlines()]
#
# # 提取所有图片中同一元素的和
label_count = dict()
# for file in line:
#     dataset = cv2.imread(osp.join(train_data, file.strip()+'.png'))
#     class_num = np.unique(dataset)
#     for num in class_num:
#         temp = np.sum(dataset == num)
#         if str(num) in label_count.keys():
#             label_count[str(num)] = label_count[str(num)] + temp
#         else:
#             label_count[str(num)] = temp
# print(label_count)

for file in os.listdir(train_data):
    dataset = cv2.imread(osp.join(train_data, file.strip()))
    class_num = np.unique(dataset)
    for num in class_num:
        temp = np.sum(dataset == num)
        if str(num) in label_count.keys():
            label_count[str(num)] = label_count[str(num)] + temp
        else:
            label_count[str(num)] = temp
print(label_count)