from osgeo import gdal, ogr, gdal_array
import numpy as np
import os
from untils.shp2ras import shp2ras
import time
import os.path as osp
from alive_progress import alive_bar
import glob

def clip_with_mask(shapefile_path, raster_path, out_path, callback = gdal.TermProgress_nocb):
    # Load the source data as a array
    srcArray = gdal_array.LoadFile(raster_path)
    if len(srcArray.shape) == 2:
        srcArray = np.expand_dims(srcArray, axis=0)

    # Also load as a gdal image to get geotransform
    # (world file) info
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    mask_name = 'temp_'+ str(int(time.time())) + '.tif'
    mask_path = os.path.join('D:/LYH/dataset/test', mask_name)
    shp2ras(shapefile_path, mask_path, snap_raster=raster_path, callback=callback)
    gdal.AllRegister()
    maskArray = gdal_array.LoadFile(mask_path)

    clip = np.multiply(maskArray, srcArray)

    gtiffDriver = gdal.GetDriverByName( 'GTiff' )
    if gtiffDriver is None:
        raise ValueError("Can't find GeoTiff Driver")
    out_ds = gtiffDriver.CreateCopy( out_path, gdal_array.OpenArray(clip, prototype_ds=raster_path),
                                     callback=callback)
    for i in range(1, out_ds.RasterCount+1):
        out_ds.GetRasterBand(i).SetNoDataValue(0)
    gdal.ErrorReset()
    os.remove(mask_path)

def batch_clip_with_mask(shpfile_path, rasterfile_path, out_path):
    shpfileList = glob.glob(shpfile_path+ '\*.shp')
    print(shpfileList)
    rasterfileList = glob.glob(rasterfile_path+ '\*.tif')
    print(rasterfileList)
    with alive_bar(len(shpfileList), force_tty=True) as bar:
        for shpefile in shpfileList:
            for rasfile in rasterfileList:
                out_name = osp.splitext(osp.basename(shpefile))[0] + '_' + osp.splitext(osp.basename(rasfile))[0] + '.tif'
                clip_with_mask(shpefile,
                               rasfile,
                               osp.join(out_path, out_name), callback=None)
                bar(1/len(rasterfileList))



def batch_clip_with_feature(shpfile_path, rasterfile_path):
    pass


if __name__ == '__main__':

    #
    # example run : $ python clip.py /<full-path>/<shapefile-name>.shp /<full-path>/<raster-name>.tif
    #
    # if len( sys.argv ) < 2:
    #     print("[ ERROR ] you must two args. 1) the full shapefile path and 2) the full raster path")
    #     sys.exit( 1 )
    #
    # main( sys.argv[1], sys.argv[2] )
    test_shpfile = r"D:\LYH\dataset\test\shp"
    test_tiffile = r"D:\LYH\dataset\test\tif"
    out_path = r'D:\LYH\dataset\test'

    # clip_with_mask(test_shpfile, test_tiffile, out_path)
    batch_clip_with_mask(test_shpfile, test_tiffile, out_path)
