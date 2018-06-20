# -*- coding: UTF-8 -*-
# @Time: 2018/6/20 4:00 PM
# Author: jixilin
# @Email: 1778202464@qq.com
# -*- coding: UTF-8 -*-
# this code for according to the shape table code column clip raster file

import arcpy
import os


def read_shp_and_clip(name_code,shape,targetfc,outmsk):
    outshp=r"in_memory/name_"+name_code
    arcpy.Select_analysis(shape,outshp, '"code" = \''+name_code+'\'')
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.cellSize =targetfc
    sd = arcpy.mapping.Layer(outshp).getExtent()
    extent = str(sd.XMin-1) + " " + str(sd.YMin-1) + " " + str(sd.XMax+1) + " " + str(sd.YMax+1)
    outmsk=os.path.join(outmsk,"a"+name_code)
    arcpy.Clip_management(targetfc, extent, outmsk, outshp, "#", "ClippingGeometry", "MAINTAIN_EXTENT")


def read_shape_table(shape,targetfc,outmsk):
    field = "code"
    cursorObj = arcpy.SearchCursor(shape)
    for row in cursorObj:
        code=row.getValue(field)
        read_shp_and_clip(code, shape, targetfc, outmsk)


if __name__ == '__main__':
    #shape file
    shapeFile = r'C:\arcgisFile\test.gdb\xibeiresult'
    #raster file
    targetfc=r'\\Mac\Home\Documents\ArcGIS\Default.gdb\Idw_csv_Fea10'#风功率密度按照0.01插值出来的idwraster
    #targetfc = r'\\Mac\Home\Documents\ArcGIS\Default.gdb\Idw_csv_Feat6' #平均风速
    #targetfc = r'\\Mac\Home\Documents\ArcGIS\Default.gdb\Idw_csv_Feat7' #风速有效小时数
    #targetfc = r'\\Mac\Home\Documents\ArcGIS\Default.gdb\Idw_csv_Feat8' #天文辐射
    #targetfc = r'\\Mac\Home\Documents\ArcGIS\Default.gdb\Idw_csv_Feat9'  # 有效天文辐射小时数
    #out clip raster floder
    outmsk=r'C:\arcgisFile\qiqi\windpowerdensity.gdb'
    readShapeTable(shapeFile,targetfc,outmsk)