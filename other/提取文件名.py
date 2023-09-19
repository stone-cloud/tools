import glob
import os
import pandas as pd

root = r'Z:\光学组\WX_JS\raw_image'

file_list = glob.glob(root + '\*\*.tif')
data = {'type':[], 'name':[], 'path':[]}

for file in file_list:
    data['type'].append(os.path.basename(file).split('_')[0])
    data['name'].append(os.path.basename(file)[:45])
    data['path'].append(file)

df = pd.DataFrame(data)
df.to_excel('进度表.xlsx', index=True, index_label='ID')