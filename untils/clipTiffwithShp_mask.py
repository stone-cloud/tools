import glob
import os
import os.path as osp
import time
from pathlib import Path
from typing import Optional

import numpy as np
from alive_progress import alive_bar
from osgeo import gdal, gdal_array

from untils.shp2ras import shp_to_ras

TEMP_PATH = './temp'
def clip_with_mask(shapefile_path: [Path, str],
                   raster_path: [Path, str],
                   out_path: [Path, str],
                   callback: Optional[object] = gdal.TermProgress_nocb,
                   temp_path: Optional[Path] = TEMP_PATH):
    """
    This function will convert shapefile to a binary mask, then to extract a portion of a raster based on the mask.
    Args:
        shapefile_path (Path, str): the shapefile path that you want to clip the raster
        raster_path (Path, str): the raster dataset path that you want to clip
        out_path (Path, str): The name and loction for the datasset you are creating
        callback (:obj:'gdal.TermProgress_nocb', Optional): callback method, you can define a new progress fucntion
         to print processing status, or use gdal.TermProgress_nocb to display the progress of processing.
        temp_path (Path, Optional): The path where temporary files are stored during processing.
         Defaults to FALSE.

    Returns: None

    """
    # Load the source data as a array
    srcArray = gdal_array.LoadFile(raster_path)
    if len(srcArray.shape) == 2:
        srcArray = np.expand_dims(srcArray, axis=0)

    # Also load as a gdal image to get geotransform
    # (world file) info
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    os.makedirs(temp_path, exist_ok=True)
    mask_name = 'temp_'+ str(int(time.time())) + '.tif'
    mask_path = os.path.join(temp_path, mask_name)
    shp_to_ras(shapefile_path, mask_path, snap_raster=raster_path, callback=callback)
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
    os.removedirs(temp_path)

def batch_clip_with_mask(shpfile_root: [Path, str],
                         raster_root: [Path, str],
                         out_path: [Path, str]):
    """
    batch clip
    Args:
        shpfile_root (Path, str): the shapefile path that you want to clip the raster
        raster_root (Path, str): the raster dataset path that you want to clip
        out_path (Path, str): The loction for the datasset you are creating

    Returns: None

    """
    shpfileList = glob.glob(shpfile_root+ '\*.shp')
    print(shpfileList)
    rasterfileList = glob.glob(raster_root+ '\*.tif')
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
