from osgeo import gdal, ogr
from pathlib import Path
from typing import Optional

def shp2ras(shp_path: Path,
            out_path: Path,
            pixel_size: float,
            field: str,
            NoData: float=0,
            data_type: Optional[object] = gdal.GDT_Byte,
            all_touch: Optional[str] = 'False',
            snap: Optional[bool] = False,
            raster: Optional[Path] = None) -> None:
    """Burn geometries from the specified list of layer into raster. If you want to konw more details, please refer
    to the following link.
    <https://www.osgeo.cn/gdal/api/gdal_alg.html?highlight=rasterizelayer#_CPPv419GDALRasterizeLayers12GDALDatasetHi
    PiiP9OGRLayerH19GDALTransformerFuncPvPdPPc16GDALProgressFuncPv>

    Args:
        shp_path (str): The shpfile path that will be convert raster image.
        out_path (str): Save path for output raster.
        pixel_size (float):  The resolution of shpfile when converted to raster image.
        field (str): Identifies an attribute field on the features to be used for a burn in value.
            The value will be burned into all output bands. If specified, padfLayerBurnValues will not
            be used and can be a NULL pointer.
        NoData (float): Nodata value for output raster
        data_type (str, optional): Data type of the output data array.inclouding "gdal.GDT_Byte, gdal.GDT_Int16,
            gdal.GDT_UInt16, gdal.GDT_Int32, gdal.GDT_UInt32, gdal.GDT_Float32, gdal.GDT_Float64,
            gdal.GDT_CFloat32, gdal.GDT_CFloat64". Defaults to gdal.GDT_Byte.
        all_touch (:obj:'osgeo._gdalconst', optional): May be set to TRUE to set all pixels touched by the line
            or polygons, not just those whose center is within the polygon or that are selected by brezenhams line
            algorithm. Defaults to FALSE.
        snap (bool, optional):
        raster (str, optional):

    Returns:
        None
    """

    # if isinstance(data_type, str):
    #     data_type = data_type
    # elif isinstance(data_type, int):
    #     data_type = DATA_TYPE[data_type]
    # else:
    #     raise NotImplementedError
    assert shp_path, 'shp_path cannot be empty'
    assert out_path, 'out_path is empty, please check it.'
    shpfile = ogr.Open(shp_path, 0)
    lyer = shpfile.GetLayer()
    x_min, x_max, y_min, y_max = lyer.GetExtent()
    if snap and raster:
        snap_ras = gdal.Open(raster)
        snap_ras_trans = snap_ras.GetGeoTransform()
        snap_ras_proj = snap_ras.GetProjection()
        # x_pixel_size, y_pixel_size = snap_ras_trans[1], abs(snap_ras_trans[5])
        x_res = snap_ras.RasterXSize
        y_res = snap_ras.RasterYSize
        # snap_x_min, sanp_y_max = snap_ras_trans[0], snap_ras_trans[3]

        # if ((x_min - snap_x_min) % x_pixel_size) != 0 or ((y_max - sanp_y_max) % y_pixel_size) != 0:
        #     x_min = x_min + x_pixel_size - (x_min - snap_x_min) % x_pixel_size
        #     y_max = y_max + y_pixel_size - (y_max - sanp_y_max) % y_pixel_size
        # x_res = int((x_max - x_min) / x_pixel_size)
        # y_res = int((y_max - y_min) / y_pixel_size)
        target_ds = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, 1, data_type,
                                                         options=['BigTIFF=YES', 'TILED=YES', 'COMPRESS=LZW'])
        target_ds.SetGeoTransform(snap_ras_trans)
        # target_ds.SetGeoTransform((snap_x_min, x_pixel_size, 0, sanp_y_max, 0, -y_pixel_size))
        # target_ds.SetProjection(snap_ras_proj)
        # del snap_ras
    else:
        if pixel_size:
            x_res = int((x_max - x_min) / pixel_size)
            y_res = int((y_max - y_min) / pixel_size)
            target_ds = gdal.GetDriverByName('GTiff').Create(out_path, x_res, y_res, 1, gdal.GDT_Byte,
                                                             options=['BigTIFF=YES', 'TILED=YES', 'COMPRESS=LZW'])
            target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
        else:
            raise AttributeError

    # target_ds.SetProjection(data.GetProjection())
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(NoData)
    if field:
        print(1)
        gdal.RasterizeLayer(target_ds, [1], lyer,
                            options=["ALL_TOUCHED="+all_touch,"ATTRIBUTE="+field], callback=gdal.TermProgress_nocb)
    else:
        print(2)
        gdal.RasterizeLayer(target_ds, [1], lyer, burn_values=[1],
                            options=["ALL_TOUCHED=" + all_touch], callback=gdal.TermProgress_nocb)

    del target_ds
    shpfile.Release()

if __name__ == '__main__':
    shp_root = r"D:\LYH\dataset\greenhouse\raw_data\pengzhou\shp\澎州_大棚_优化后.shp"
    out_root = r'D:\LYH\dataset\greenhouse\raw_data\pengzhou\shp\pengzhoudapeng_label.tif'
    # out_root1 = r'D:\LYH\dataset\test_data\111\江西赣州宁都县222.tif'
    ras_root = r"D:\LYH\dataset\greenhouse\raw_data\pengzhou\彭州_19_raw.tif"
    # mkdir_or_exist(shp_out_root)
    # ras_list = glob.glob(ras_root + '\*.tif')
    # ras_list = [os.path.join(ras_root, 'GF6_PMS_20230401_L1A1420305843_cut_0616_20000id.tif')]
    # with alive_bar(len(ras_list), force_tty=True) as bar:
    # print('共读取影像%d景' %len(ras_list))
    shp2ras(shp_root, out_root, pixel_size=None, field=None, NoData=0, snap=True, raster=ras_root)
    # shp2ras(shp_root, out_root, pixel_size=0.000026, field='gridcode', NoData=0, snap=False, raster=ras_root)