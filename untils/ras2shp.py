from osgeo import gdal, osr, ogr
import os
import glob
import os.path as osp
from pathlib import Path

# def progress_cb(complete, message, cb_data):
#     '''Emit progress report in numbers for 10% intervals and dots for 3%'''
    # with alive_bar(force_tty=True, manual=True) as bar:
    #     bar(complete)
    # if int(complete*100) % 10 == 0:
    #     print(f'{complete*100:.0f}', end='', flush=True)
    # elif int(complete*100) % 3 == 0:
    #     print(f'{cb_data}', end='', flush=True)

def ras_to_shp(raster: Path, out_path: Path, **kwargs) -> str:
    out_shp = os.path.join(out_path, os.path.basename(raster).replace(".tif", ".shp"))
    in_raster = gdal.Open(raster)  # 读取路径中的栅格数据
    in_band = in_raster.GetRasterBand(1)  # 这个波段就是最后想要转为矢量的波段，如果是单波段数据的话那就都是1
    prj = osr.SpatialReference()
    prj.ImportFromWkt(in_raster.GetProjection())  # 读取栅格数据的投影信息，用来为后面生成的矢量做准备

    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(out_shp):  # 若文件已经存在，则删除它继续重新做一遍
        drv.DeleteDataSource(out_shp)
    Polygon = drv.CreateDataSource(out_shp)  # 创建一个目标文件
    Poly_layer = Polygon.CreateLayer(raster[:-4], srs=prj, geom_type=ogr.wkbMultiPolygon)  # 对shp文件创建一个图层，定义为多个面类
    value_Field = ogr.FieldDefn('value', ogr.OFTReal)  # 给目标shp文件添加一个字段，用来存储原始栅格的pixel value
    # area_Field = ogr.FieldDefn('area', ogr.OFTReal)
    Poly_layer.CreateField(value_Field)
    # Poly_layer.CreateField(area_Field)
    # Poly_layer.GetLayerDefn().AddFieldDefn(area_Field)
    gdal.FPolygonize(in_band, None, Poly_layer, 0, callback=gdal.TermProgress_nocb)  # 核心函数，执行的就是栅格转矢量操作
        # bar(pro)
    # for feature in Poly_layer:
    #     print(feature.GetFieldIndex('area'))
    #     print(feature.geometry().GetArea())
    #     # feature.SetField(feature.GetFieldIndex('area'), feature.geometry().GetArea())
    #     # Poly_layer.CreateFeature(feature)
    # print(Poly_layer.GetLayerDefn().GetFieldDefn(0).name)
    # print(Poly_layer.GetLayerDefn().GetFieldDefn(1).name)
    Poly_layer.SetAttributeFilter('value=0')
    for feature in Poly_layer:
        Poly_layer.DeleteFeature(feature.GetFID())
    Polygon.SyncToDisk()
    # Polygon.SyncToDisk()
    Polygon.Destroy()
    Polygon = None
    return Polygon

def mkdir_or_exist(dir_name: Path, mode=0o777):
    if dir_name == '':
        return
    dir_name = osp.expanduser(dir_name)
    os.makedirs(dir_name, mode=mode, exist_ok=True)

if __name__ == '__main__':
    ras_root = r"D:\LYH\0811\other"
    shp_out_root = r'D:\LYH\0811\watershp1'
    mkdir_or_exist(shp_out_root)
    ras_list = glob.glob(ras_root + '\*.tif')
    # ras_list = [os.path.join(ras_root, 'GF6_PMS_20230401_L1A1420305843_cut_0616_20000id.tif')]
    # with alive_bar(len(ras_list), force_tty=True) as bar:
    print('共读取影像%d景' %len(ras_list))
    for i, ras in enumerate(ras_list):
        print(f'第{i+1}景', os.path.basename(ras), '正在处理')
        ras_to_shp(ras, shp_out_root)
