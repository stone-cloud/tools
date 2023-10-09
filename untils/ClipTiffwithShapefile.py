import operator
from functools import reduce
from osgeo import gdal, ogr, osr, gdal_array
from PIL import Image, ImageDraw
import os, sys
import numpy as np
gdal.UseExceptions()


# This function will convert the rasterized clipper shapefile
# to a mask for use within GDAL.
def imageToArray(i):
    """
    Converts a Python Imaging Library array to a
    gdalnumeric image.
    """
    a = np.asarray(i)
    # a=np.fromstring(i.tostring(),'b')
    # a.shape=i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
    """
    Converts a gdalnumeric array to a
    Python Imaging Library Image.
    """
    i=Image.fromarray(a)
    return i

def world2Pixel(geoMatrix, x, y):
  """
  Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
  the pixel location of a geospatial coordinate
  """
  ulX = geoMatrix[0]
  ulY = geoMatrix[3]
  xDist = geoMatrix[1]
  yDist = geoMatrix[5]
  rtnX = geoMatrix[2]
  rtnY = geoMatrix[4]
  pixel = int((x - ulX) / xDist)
  line = int((ulY - y) / xDist)
  return (pixel, line)

#
#  EDIT: this is basically an overloaded
#  version of the gdal_array.OpenArray passing in xoff, yoff explicitly
#  so we can pass these params off to CopyDatasetInfo
#
def OpenArray( array, prototype_ds = None, xoff=0, yoff=0 ):
    ds = gdal_array.OpenNumPyArray(array, True)

    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal.Open( prototype_ds )
        if prototype_ds is not None:
            gdal_array.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff )
    return ds

def histogram(a, bins=range(0,256)):
  """
  Histogram function for multi-dimensional array.
  a = array
  bins = range of numbers to match
  """
  fa = a.flat
  n = np.searchsorted(np.sort(fa), bins)
  n = np.concatenate([n, [len(fa)]])
  hist = n[1:]-n[:-1]
  return hist

def stretch(a):
  """
  Performs a histogram stretch on a gdalnumeric array image.
  """
  hist = histogram(a)
  im = arrayToImage(a)
  lut = []
  for b in range(0, len(hist), 256):
    # step size
    step = reduce(operator.add, hist[b:b+256]) / 255
    # create equalization lookup table
    n = 0
    for i in range(256):
      lut.append(n / step)
      n = n + hist[i+b]
  im = im.point(lut)
  return imageToArray(im)

def clip_main(shapefile_path, raster_path, out_path):
    # Load the source data as a array
    srcArray = gdal_array.LoadFile(raster_path)
    if len(srcArray.shape) == 2:
        srcArray = np.expand_dims(srcArray, axis=0)

    # Also load as a gdal image to get geotransform
    # (world file) info
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    # Create an OGR layer from a boundary shapefile
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer( os.path.split( os.path.splitext( shapefile_path )[0])[1])
    # poly = lyr.GetNextFeature()

    # Convert the layer extent to image pixel coordinates
    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    # Calculate the pixel size of the new image
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)

    clip = srcArray[:, ulY:lrY, ulX:lrX]

    #
    # EDIT: create pixel offset to pass to new image Projection info
    #
    xoffset = ulX
    yoffset = ulY
    print("Xoffset, Yoffset = ( %f, %f )" % ( xoffset, yoffset ))

    # Create a new geomatrix for the image
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    # Map points to pixels for drawing the
    # boundary on a blank 8-bit,
    # black and white, mask image.
    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    for i, poly in enumerate(lyr):
        points = []
        pixels = []
        geom = poly.GetGeometryRef()
        pts = geom.GetGeometryRef(0)
        for p in range(pts.GetPointCount()):
            points.append((pts.GetX(p), pts.GetY(p)))
        for p in points:
            pixels.append(world2Pixel(geoTrans, p[0], p[1]))
        rasterize = ImageDraw.Draw(rasterPoly)
        rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)
    mask = np.logical_not(mask)

    # Clip the image using the mask
    # clip = np.choose(mask, \
    #     (clip, 0)).astype(np.float32)
    clip = np.multiply(mask, clip)
    # This image has 3 bands so we stretch each one to make them
    # visually brighter
    # for i in range(3):
    #   clip[i,:,:] = stretch(clip[i,:,:])
    # clip[:, :] = stretch(clip[:, :])
    # Save new tiff
    #
    #  EDIT: instead of SaveArray, let's break all the
    #  SaveArray steps out more explicity so
    #  we can overwrite the offset of the destination
    #  raster
    #
    ### the old way using SaveArray
    #
    # gdal_array.SaveArray(clip, "OUTPUT.tif", format="GTiff", prototype=raster_path)
    #
    ###
    #
    gtiffDriver = gdal.GetDriverByName( 'GTiff' )
    if gtiffDriver is None:
        raise ValueError("Can't find GeoTiff Driver")
    out_ds = gtiffDriver.CreateCopy( out_path, \
        OpenArray( clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset )
    )
    for i in range(1, out_ds.RasterCount+1):
        out_ds.GetRasterBand(i).SetNoDataValue(0)

    # Save as an 8-bit jpeg for an easy, quick preview
    # clip = clip.astype(np.uint8)
    # gdal_array.SaveArray(clip, "OUTPUT.jpg", format="JPEG")
    # gdal_array.SaveArray(clip, "OUTPUT.tif", format="GTiff", prototype=raster_path)
    gdal.ErrorReset()


if __name__ == '__main__':

    #
    # example run : $ python clip.py /<full-path>/<shapefile-name>.shp /<full-path>/<raster-name>.tif
    #
    # if len( sys.argv ) < 2:
    #     print("[ ERROR ] you must two args. 1) the full shapefile path and 2) the full raster path")
    #     sys.exit( 1 )
    #
    # main( sys.argv[1], sys.argv[2] )
    test_shpfile = r"D:\LYH\dataset\test_data\New_Shapefile_Erase.shp"
    test_tiffile = r"D:\LYH\dataset\test_data\raw\GF1B_5365_Clip.tif"
    out_path = r'D:\LYH\dataset\test\test_clip.tif'

    clip_main(test_shpfile, test_tiffile, out_path)