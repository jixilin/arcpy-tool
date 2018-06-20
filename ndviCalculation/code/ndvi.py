# -*- coding: UTF-8 -*-
# @Time: 2018/6/20 2:55 PM
# Author: jixilin
# @Email: 1778202464@qq.com
# -*- coding: UTF-8 -*-
import arcpy
import time
import os
'''
批量一次性计算年的ndvi和月的ndvi并完成裁剪出图的整个运算过程，需要配置模板并将所需要的遥感数据放到相应的文件夹
'''
def getSourceValue(filepath):
    pathDir = os.listdir(filepath)
    yearmax = []
    monthmax = []
    monthresult=[]
    yearresult=[]
    sourceraster=[]
    clipresult=[]
    clipresultmap=[]
    for allDir in pathDir:
        child = os.path.join(filepath, allDir)
        if allDir=='yearresult':
            yearresult.append(child)
        elif allDir=='monthresult':
            monthresult.append(child)
        elif allDir == 'yearmax':
            yearmax.append(child)
        elif allDir == 'monthmax':
            monthmax.append(child)
        elif allDir=='clipresult':
            clipresult.append(child)
        elif allDir=='clipresultmap':
            clipresultmap.append(child)
        else:
            sourceraster.append(child)
    object={'yearmax':yearmax,'monthmax':monthmax,'monthresult':monthresult,
            'yearresult':yearresult,'sourceraster':sourceraster,'clipresult':clipresult,'clipresultmap':clipresultmap}
    return object
def getMoudleValue(filepath):
    pathDir = os.listdir(filepath)
    clippath=''
    monthmaxndvi=''
    yearmaxndvi=''
    clipresultmap=''
    for allDir in pathDir:
        child = os.path.join(filepath, allDir)
        if allDir=='clip.mxd':
            clippath=child
        elif allDir=='yearmaxndvimoudle.mxd':
            yearmaxndvi = child
        elif allDir == 'monthmaxndvimoudle.mxd':
            monthmaxndvi = child
        elif allDir=='clipresultmapmoudle.mxd':
            clipresultmap=child
    object={'clippath':clippath,'monthmaxndvi':monthmaxndvi,'yearmaxndvi':yearmaxndvi,'clipresultmap':clipresultmap}
    return object
def combinationData(sourceValue,moudleValue,gansulayer):
    sourcerasters = sourceValue['sourceraster']
    arcpy.AddMessage("begin clip data")
    for months in sourcerasters:
        monthPaths=os.listdir(months)
        monthkeys = []
        for month in monthPaths:
            suffix=os.path.splitext(month)[1]
            if suffix=='.tif':
                monthPath=os.path.join(months,month)
                monthkeys.append(monthPath)
        print monthkeys
        extractByMaskData(monthkeys,sourceValue,moudleValue,gansulayer)
        # clipData(monthkeys,sourceValue,moudleValue,gansulayer)
    arcpy.AddMessage("end clip data")
    return True
def isExitFold(outname):
    isExists = os.path.exists(outname)
    if not isExists:
        os.makedirs(outname)
def clipData(monthkeys,sourceValue,moudleValue,gansulayer):
    clipResult=sourceValue['clipresult'][0]
    mxdPath = moudleValue['clippath']
    mxd = arcpy.mapping.MapDocument(mxdPath)
    df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
    layer = arcpy.mapping.ListLayers(mxd, 'gansumian', df)[0]
    sd = layer.getExtent()
    extent = str(sd.XMin) + " " + str(sd.YMin) + " " + str(sd.XMax) + " " + str(sd.YMax)
    sourcerasters=monthkeys
    for month in sourcerasters:
        sourcename=os.path.splitext(month)[0]
        sourcename=sourcename.split('//')
        monthkey=sourcename[len(sourcename)-2]
        sourcename=sourcename[len(sourcename)-1]+os.path.splitext(month)[1]
        outname = os.path.join(clipResult,monthkey,sourcename)
        outflod=os.path.join(clipResult,monthkey)
        isExitFold(outflod)
        month = arcpy.mapping.Layer(month)
        arcpy.mapping.AddLayer(df, month, "BOTTOM")
        source = arcpy.mapping.ListLayers(mxd,sourcename, df)[0]
        isExists = os.path.exists(outname)
        if not isExists:
            arcpy.Clip_management(source, extent, outname, layer, "#", "ClippingGeometry", "MAINTAIN_EXTENT")
def extractByMaskData(monthkeys,sourceValue,moudleValue,gansulayer):
    clipResult = sourceValue['clipresult'][0]
    sourcerasters = monthkeys
    for month in sourcerasters:
        source=month
        sourcename = os.path.splitext(month)[0]
        sourcename = sourcename.split('\\')
        monthkey = sourcename[len(sourcename) - 2]
        sourcename = sourcename[len(sourcename) - 1] + os.path.splitext(month)[1]
        outname = os.path.join(clipResult, monthkey, sourcename)
        outflod = os.path.join(clipResult, monthkey)
        isExitFold(outflod)
        isExists = os.path.exists(outname)
        if not isExists:
            arcpy.CheckOutExtension("Spatial")
            outExtractByMask = arcpy.sa.ExtractByMask(source, gansulayer)
            outExtractByMask.save(outname)
def OnlyNum(s, oth=''):
    s2 = s
    fomart = '0123456789'
    for c in s2:
        if not c in fomart:
            s = s.replace(c, '')
    return s
def combinationClip(sourceValue,moudleValue):
    clipPath=sourceValue['clipresult'][0]
    arcpy.AddMessage("begin monthmax ndvi and out clipresultmap")
    for months in os.listdir(clipPath):
        monthPaths=os.path.join(clipPath,months)
        oneMonth=[]
        count = 0
        for month in os.listdir(monthPaths):
            suffix = os.path.splitext(month)[1]
            if suffix == '.tif':
                sourcename = os.path.splitext(month)[0]
                sourcename = sourcename.split('\\')
                count+=1
                if count%2!=0:
                    monthkey = sourcename[len(sourcename) - 2]
                    monthkey=str(monthkey)[0:6]
                    monthmaxPath = sourceValue['monthmax'][0]
                    monthmaxPath=os.path.join(monthmaxPath,monthkey+".tif")
                onemonthPaths = os.path.join(monthPaths,month)
                oneMonth.append(onemonthPaths)
                outPath=os.path.join(sourceValue['clipresultmap'][0])
                clipresultmapmoudle = moudleValue['clipresultmap']
                outmaps(clipresultmapmoudle,onemonthPaths,'clipresultmap',outPath)
        maxNdvi(oneMonth,monthmaxPath)
    arcpy.AddMessage("end monthmax ndvi and end out clipresultmap")
    arcpy.AddMessage("begin yearmax ndvi")
    monthmaxPath = sourceValue['monthmax'][0]
    monthDatas=[]
    for month in os.listdir(monthmaxPath):
        onemonthPaths = os.path.join(monthmaxPath, month)
        suffix = os.path.splitext(month)[1]
        if suffix == '.tif':
            monthDatas.append(onemonthPaths)
    yearMaxPath=sourceValue['yearmax'][0]
    yearKey=OnlyNum(yearMaxPath)
    yearMaxPath=os.path.join(yearMaxPath,yearKey+".tif")
    maxNdvi(monthDatas,yearMaxPath)
    arcpy.AddMessage("end yearmax ndvi")
def maxNdvi(data,outname):
    outdata = arcpy.sa.CellStatistics(data, "MAXIMUM", "DATA")
    isExists = os.path.exists(outname)
    if not isExists:
        outdata.save(outname)
def returnMonth(month):
    current=int(month)
    returnValue=month
    if current<10:
        returnValue=month[1]
    return returnValue
def outmaps(mxdpath,target,style,out):
    key = OnlyNum(target)
    if style=='monthmaxndvi':
        monthkey=returnMonth(str(key[8:10]))
        mapName = key[0:4]+u'年'+monthkey+u'月归一化植被指数图'
    elif style=='yearmaxndvi':
        mapName = key[0:4]+u'年归一化植被指数图'
    elif style=='clipresultmap':
        temptarget=os.path.basename(target)
        key = OnlyNum(temptarget)
        monthkey = returnMonth(str(key[4:6]))
        dayakey=returnMonth(str(key[6:8]))
        mapName = key[0:4] + u'年' + monthkey + u'月'+dayakey+u'日归一化植被指数图'
        style='monthmaxndvi'
    MapPath = os.path.join(out, mapName + '.jpg')
    mxd = arcpy.mapping.MapDocument(mxdpath)
    df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
    target = arcpy.mapping.Layer(target)
    lyrFile = arcpy.mapping.ListLayers(mxd, style, df)[0]
    arcpy.mapping.InsertLayer(df,lyrFile,target, 'BEFORE')
    target = arcpy.mapping.ListLayers(mxd,target.name, df)[0]
    arcpy.mapping.UpdateLayer(df, target, lyrFile, True)
    mapname = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", 'mapname')[0]
    mapname.text = mapName
    isExists = os.path.exists(MapPath)
    if not isExists:
        arcpy.mapping.ExportToJPEG(mxd,MapPath,resolution=400)
def combinationMax(sourceValue,moudleValue):
    yearMaxPath = sourceValue['yearmax'][0]
    monthresult=sourceValue['monthresult'][0]
    yearresult=sourceValue['yearresult'][0]
    monthmaxPath = sourceValue['monthmax'][0]
    monthmaxndvi=moudleValue['monthmaxndvi']
    yearmaxndvi=moudleValue['yearmaxndvi']
    Parameters=[]
    arcpy.AddMessage("begin outmap month")
    for month in os.listdir(monthmaxPath):
        onemonthPaths = os.path.join(monthmaxPath, month)
        suffix = os.path.splitext(month)[1]
        if suffix == '.tif':
            Parameters.append((monthmaxndvi,onemonthPaths,'monthmaxndvi',monthresult))
            outmaps(monthmaxndvi,onemonthPaths,'monthmaxndvi',monthresult)
    arcpy.AddMessage("end outmap month")
    arcpy.AddMessage("begin outmap year")
    for year in os.listdir(yearMaxPath):
        oneyearPaths = os.path.join(yearMaxPath, year)
        suffix = os.path.splitext(year)[1]
        if suffix == '.tif':
            Parameters.append((yearmaxndvi,oneyearPaths, 'yearmaxndvi',yearresult))
            outmaps(yearmaxndvi,oneyearPaths, 'yearmaxndvi',yearresult)
    arcpy.AddMessage("end outmap year")
def mainOutMap(sourcePath,moudlePath,gansulayer):
    sourcePath=getSourceValue(sourcePath)
    moudlePath=getMoudleValue(moudlePath)
    isClip = combinationData(sourcePath,moudlePath, gansulayer)
    if isClip:
        combinationClip(sourcePath,moudlePath)
    combinationMax(sourcePath, moudlePath)
if __name__ == '__main__':
    start = time.time()
    sourcePath=r'C:/arcgisFile/yaogan/2013'
    # sourcePath=arcpy.GetParameterAsText(0)
    # print getSourceValue(sourcePath)
    moudlePath = r"C:/arcgisFile/yaogan/mapmoudle/mapmxd"
    # moudlePath =arcpy.GetParameterAsText(1)
    gansulayer=r'C:\arcgisFile\yaogan\mapmoudle\mapshapsource\gansuline.shp'
    # gansulayer=arcpy.GetParameterAsText(2)
    # print getMoudleValue(moudlePath)
    mainOutMap(sourcePath,moudlePath,gansulayer)
    # if isClip:
    #     maxNdvi(getSourceValue(sourcePath),getMoudleValue(moudlePath))
    # maxNdvi(getSourceValue(sourcePath), getMoudleValue(moudlePath))
    end = time.time()
    currenttime=end - start
    #grouptest