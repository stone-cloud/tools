import os
import os.path as osp
import cv2
import tifffile
from PIL import Image
import numpy as np

root = r'D:\LYH\dataset\greenhouse\greenhouse\labels'
out_root = r'D:\LYH\dataset\greenhouse\greenhouse\label'
for dir, _, files in os.walk(root):
    for file in files:
        newname = file[:-4].replace('_lab', '')
        img = Image.open(osp.join(dir, file))
        img = img.point(lambda x:x>0)
        print(np.unique(img))
        img.save(osp.join(out_root, newname+'.png'))