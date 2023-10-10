import os.path as osp
from pathlib import Path
from typing import Optional

from osgeo import ogr


def featue_to_shp(input_shp: [Path, str],
                  out_path: [Path, str],
                  field: Optional[str] = 'FID'):
    """
    Detach form the shape file to each feature and saved as a vector.
    Args:
        input_shp (Path, str): The shapefile path that you want to split
        out_path (Path, str): The path where the detached layer is saved as a vector.
        field (str, Optional):  The name of vector that be saved detached layer.

    Returns: None

    """
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shapef = ogr.Open(input_shp)
    lyr = shapef.GetLayer()
    print(f'the number of feature: {lyr.GetFeatureCount()}')
    for i, feature in enumerate(lyr):
        f_name = feature.GetField(field)
        out_file = driver.CreateDataSource(osp.join(out_path, f_name+'.shp'))
        out_lyr = out_file.CreateLayer(f_name+'.shp', lyr.GetSpatialRef(), ogr.wkbPolygon)
        def_feature = out_lyr.GetLayerDefn()

        geometry = feature.GetGeometryRef()
        current_union = geometry.Clone()
        current_union = current_union.Union(geometry).Clone()
        out_feature = ogr.Feature(def_feature)
        out_feature.SetGeometry(current_union)
        out_lyr.ResetReading()
        out_lyr.CreateFeature(out_feature)
        out_file.Destroy()

if __name__ == '__main__':
    shpfile = r"Z:\光学组\HN_second\data_rectangle\data_rectangle.shp"
    out_path = r'Z:\光学组\HN_second\data_rectangle\boundary'
    featue_to_shp(shpfile, out_path, 'productid')