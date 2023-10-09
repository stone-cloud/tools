from osgeo import ogr
import os.path as osp

def featue_to_shp(input_shp, out_path, field):
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
    shpfile = r"D:\LYH\dataset\test\shp\F1.shp"
    out_path = r'D:\LYH\dataset\test\shp'
    featue_to_shp(shpfile, out_path, 'category')