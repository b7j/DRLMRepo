#!/usr/bin/env python

"""
Purpose:  Extracts field data and related image window data and outputs
          according to an SQL query and outputs data in a csv file in
          the exact format required for input into Peter's calibration script.
Author:   Rebecca Trevithick
Date:     29 June 2011
"""


#----------------------------------------------------------------
# Import Modules
#----------------------------------------------------------------

import os
import qvf
import qv
import sys
from osgeo import gdal,ogr,osr
from numpy import *
import gdalcommon
import string
from rsc.utils import metadb, ogrcommon
from optparse import OptionParser
import numpy.ma as ma
from rios import applier


#---------------------------------------------------------------
# Parent Class
#---------------------------------------------------------------

class Observation(object):
    def __init__(self,sqlHeaders,sqlResults):
        for varName in sqlHeaders:
            try:
                ndx = sqlHeaders.index(varName)
                self.__dict__[varName] = sqlResults[ndx]
            except TypeError:
                self.__dict__[varName] = 'null'
        self.image = {}


class ImageDict(object):
    def __init__(self):
        self.imageName = None
        self.timeLag = None
        self.tmp3pix = None

#--------------------------------------------------------------
# Functions
#---------------------------------------------------------------
def recallList(sceneListTemp, recallStage):
    """
    Define and recall landsat images with stage
    """
    recallList = []
    for scene in sceneListTemp:
        scene = qvf.changestage(scene, recallStage)
        if not os.path.exists(scene) and qv.existsonfilestore(scene):
            recallList.append(scene)

    qv.recallToHere(recallList)


def getHeaders(description):
    """
    creates list of column headers from sql query.
    """
    headers = []
    dataTypes = []
    for desc in description:
        header = desc[0]
        dataType = desc[1]
        headers.append(header)

    return headers



def getFieldPoints(sql):
    """
    Function to return locations of field points from database according
    to sql query.
    """

    pointDict = {}

    if sql is None:
       sql = """
            SELECT fractional.obs_key, fractional.obs_time::date, fractional.site,
                ST_X(field_geom.geom) as longitude,
                ST_Y(field_geom.geom) as latitude,
                crust, dist, rock, green, crypto, dead, litter, mid_g,
                mid_d, mid_b, crn, over_g, over_d, over_b, persist_gr, num_points
            FROM fractional, field_geom, states
            WHERE field_geom.obs_key = fractional.obs_key
            AND st_intersects(field_geom.geom,states.geom)
            AND states.state_name = 'NT'
           
            """

    con = metadb.connect(api=metadb.DB_API)
    cursor = con.cursor()
    cursor.execute(sql)
    description = cursor.description
    headers = getHeaders(description)

    points = cursor.fetchall()

    return points, headers



def searchDatabaseScenes(pointDict,timeLag,defStage,winsize):
    """
    Search database to find scenes which intersect field data points and were acquired
    within specified number of days of field work
    """

    keys = pointDict.keys()

    for key in keys:
        pointDict[key].image[1] = ImageDict()
        pointDict[key].image[2] = ImageDict()
        pointDict[key].image[3] = ImageDict()
        pointDict[key].image[4] = ImageDict()
        pointDict[key].image[5] = ImageDict()
        pointDict[key].image[6] = ImageDict()
        pointDict[key].image[7] = ImageDict()
        pointDict[key].image[8] = ImageDict()


    for stage in ['d%s' % defStage]:
        if stage == 'd%s' % defStage:
            recallStage = 'd%s' % defStagel 
            data_source = 'usgs'

        for key in keys:
            fieldDate = pointDict[key].obs_time.split(' ')[0]
            fieldDate = fieldDate.replace('-','')
            fieldDate = '%s-%s-%s' % (fieldDate[:4],fieldDate[4:6],fieldDate[6:])
            pointDict[key].obs_time = fieldDate

            con = metadb.connect(api=metadb.DB_API)
            cursor = con.cursor()

            query = """
                SELECT abs(cast('%s' as date) - f.cal_date),SLATSFilename(f.sat_type,f.scene_date)
                FROM FindFootprintsByPoint(%s, %s) as f, landsat_list
                WHERE landsat_list.scene_date = f.scene_date
                    AND abs(cast('%s' as date) - f.cal_date) < %s
                    AND landsat_list.product = 're'
                    AND data_source ='%s'




                    """ % (fieldDate,pointDict[key].longitude,pointDict[key].latitude,fieldDate,timeLag,data_source)
            try:
                cursor.execute(query)
                results = cursor.fetchall()

                results.sort()

                index=[1,2,3,4,5,6,7,8]

                if len(results) > 0:
                    for i in index:
                        try:
                            result = results[i-1]
                            image = qvf.changestage(result[1], '%s' % stage)

                            if qv.existsonfilestore(image) and pointDict[key].image[i].imageName is None:
                                pointDict[key].image[i].imageName = image
                                pointDict[key].image[i].timeLag = result[0]
                                pointDict[key].image[i].tmp3pix = qvf.changestage('%s_%s_%spix.tif' % (image.split('.')[0],pointDict[key].site.strip(),winsize),'tmp')
                            else:
                                pointDict[key].image[i].imageName = 'None'
                                pointDict[key].image[i].timeLag = 'None'
                                pointDict[key].image[i].tmp3pix = 'None'

                        except IndexError:
                            pointDict[key].image[i].imageName = 'None'
                            pointDict[key].image[i].timeLag = 'None'
                            pointDict[key].image[i].tmp3pix = 'None'

                            image='None'

                elif len(results) == 0:
                    image = 'None'
                    print pointDict[key].site,fieldDate,pointDict[key].longitude,pointDict[key].latitude

                else:
                    print 'Really bad problem.'

            except:
                print 'failed', query, pointDict[key].site

    return pointDict



def applyMasks(processedList):
    """
    Do masking of output - create generic model to be used for all seasonal products.
    Uses cloud and shadow masks to mask image. Uses RSC derived masks if available
    and fmask if not.
    """

    cloudList = []
    shadowList = []
    sceneList =[]
    maskImageList = []
    processedListClipped = []

    for scene in processedList:
        processedListClipped.append(qvf.changestage(scene, 'tmp'))
        if not os.path.exists(qvf.changestage(scene, 'tmp')):

            fMaskCloudImage = qvf.changestage(scene, 'dgr')

            fMaskShadowImage = qvf.changestage(scene, 'dgs')
            if qv.existsonfilestore(fMaskCloudImage):
                cloudMaskImage = fMaskCloudImage
            if qv.existsonfilestore(fMaskShadowImage):
                shadowMaskImage = fMaskShadowImage

            if qv.existsonfilestore(cloudMaskImage) and qv.existsonfilestore(shadowMaskImage) and qv.existsonfilestore(scene):
                cloudList.append(cloudMaskImage)
                shadowList.append(shadowMaskImage)
                sceneList.append(scene)
                maskImageList.append([scene,cloudMaskImage,shadowMaskImage])


    if len(maskImageList)!=0:
        recallList(cloudList, qvf.stage(cloudList[0]))
        recallList(shadowList, qvf.stage(shadowList[0]))
        recallList(sceneList, qvf.stage(sceneList[0]))

    print 'Applying masks...'

    controls = applier.ApplierControls()
    controls.setStatsIgnore(0)

    for (image1,image2,image3) in maskImageList:
        tmpscene = qvf.changestage(image1, 'tmp')
        print tmpscene

        if not os.path.exists(tmpscene) and os.path.exists(image1) and os.path.exists(image2):
            infiles = applier.FilenameAssociations()
            infiles.image1 = image1
            infiles.image2 = image2
            infiles.image3 = image3
            outfiles = applier.FilenameAssociations()
            outfiles.outimage = tmpscene
            if not os.path.exists(outfiles.outimage):
                applier.apply(createMaskedImage, infiles, outfiles, controls=controls)
            if os.path.exists(outfiles.outimage):

                os.remove(image1)
                os.remove(image2)
                os.remove(image3)

    return  processedListClipped


def createMaskedImage(info, inputs, outputs):
    """
    create an cloud masked image
    """
    temp = where(inputs.image2==1,inputs.image1,0)
    outputs.outimage = where(inputs.image3==1,temp,0)


def getFileList(pointDict,winsize):
    """
    Creates a list of files needing to be recalled.
    """
    fileList=[]

    keys = pointDict.keys()

    for key in keys:
        for imageKey in range(1,9):
            imageName=pointDict[key].image[imageKey].imageName
            tmpName=pointDict[key].image[imageKey].tmp3pix
            if imageName!= None and imageName!='None' and not os.path.exists(tmpName):
                fileList.append(imageName)
    return fileList




def getStatistics(pointDict,winsize,statistic):
    """
    Calls function that determines means for sites with valid image and
    appends result to dictionary.
    """
    i=0
    keys = pointDict.keys()
    for key in keys:
        i=i+1

        for imageKey in range(1,9):

            imageRef=pointDict[key].image[imageKey]
            if statistic == 'mean': imageRef.imageMean = 'None'
            elif statistic == 'std': imageRef.imageStd = 'None'

            (band1,band2,band3,band4,band5,band6,count) =(getStatVal(imageRef.imageName,
                pointDict[key].longitude,pointDict[key].latitude,
                winsize,statistic,pointDict[key].site))

            if statistic == 'mean':
                imageRef.imageMean = ('%s,%s,%s,%s,%s,%s' % (band1,band2,band3,band4,band5,band6))

            elif statistic == 'std':
                imageRef.imageStd = ('%s,%s,%s,%s,%s,%s' % (band1,band2,band3,band4,band5,band6))

            imageRef.count = count

    return pointDict



def getStatVal(imageFile,longitude,latitude,winsize,statistic,site):
    """
    Caculates the statistics on the pixels in the window array
    """

    band1,band2,band3,band4,band5,band6,count = 'None','None','None','None','None','None','None'

    if imageFile != 'None' and imageFile != None:
        imageFile=qvf.changestage(imageFile,'tmp')
        temp = '%s_%s_%spix.tif' % (imageFile.split('.')[0],site.strip(),winsize)

        if not os.path.exists(temp):
            subsetRaster = getWindow(imageFile,longitude,latitude,winsize,site)
        else:
            subsetRaster = temp

        try:
            imgInfo = gdalcommon.info(subsetRaster)
            handle = gdal.Open(subsetRaster)

            for band in [1,2,3,4,5,6]:
                if handle != None:
                    bandHandle = handle.GetRasterBand(band)
                    bandArray = bandHandle.ReadAsArray()

                    maskedBand = ma.masked_values(bandArray, 0)
                    count = ma.count(maskedBand)

                    if statistic == 'mean': statVal = maskedBand.mean()
                    elif statistic == 'std': statVal = maskedBand.std()
                    else:
                        statVal = None

                    if band == 1:
                        band1 = statVal

                    elif band == 2:
                        band2 = statVal

                    elif band == 3:
                        band3 = statVal

                    elif band == 4:
                        band4 = statVal

                    elif band == 5:
                        band5 = statVal

                    elif band == 6:
                        band6 = statVal
        except:
            pass

    return band1, band2, band3, band4, band5, band6, count





def getWindow(imageFile,x,y,winsize,site):
    """
    Extracts portion of raster defined by window as an array.
    """

    inProj = osr.SpatialReference()
    inProj.ImportFromEPSG(int('4326'))

    outProj = osr.SpatialReference()
    outProj.ImportFromEPSG(int('2835%s' % qvf.utmzone(imageFile)[-1]))

    transform = osr.CoordinateTransformation(inProj, outProj)

    (x, y, z) = transform.TransformPoint(x, y)
    x = float(x)
    y = float(y)
    winsize = int(cmdargs.winsize)
    imgInfo = gdalcommon.info(imageFile)
    trans = imgInfo.transform
    bands = imgInfo.rasterCount

    (row,col) = gdalcommon.eastNorth2rowCol(trans,x,y)
    (row,col) = (int(row), int(col))

    temp = '%s_%s_%spix.tif' % (imageFile.split('.')[0],site.strip(),winsize)

    cmd = 'gdal_translate -srcwin %s %s %s %s %s %s' % (col-int(.5*winsize), row-int(.5*winsize), winsize, winsize, imageFile, temp)
    os.system(cmd)

    return temp



def outCsv(pointDict,headers,output,analyse):
    """
    Output results in csv file.
    """

    csvHandle = open('%s.csv' % (output),'w')
    csvHandle.write('%s,image,timelag,band1,band2,band3,band4,band5,band6,band1,band2,band3,band4,band5,band6,count\n' % (','.join(['%s' % x for x in headers])))

    keys = pointDict.keys()
    for key in keys:

        imageKeys = pointDict[key].image.keys()
        for imageKey in imageKeys:
            try:
                fieldString = ('%s,%s,%s,%s,%s,%s\n' % (','.join([('%s' % str(pointDict[key].__dict__[varName]).strip()) for varName in headers]),pointDict[key].image[imageKey].imageName,pointDict[key].image[imageKey].timeLag,pointDict[key].image[imageKey].imageMean,pointDict[key].image[imageKey].imageStd,pointDict[key].image[imageKey].count))
            except AttributeError:
                fieldString = ('%s,%s,%s,%s,%s,%s\n' % (','.join([('%s' % str(pointDict[key].__dict__[varName]).strip()) for varName in headers]),pointDict[key].image[imageKey].imageName,pointDict[key].image[imageKey].timeLag,'None','None','None'))

            csvHandle.write(fieldString)
            fieldList=fieldString.split(',')

    csvHandle.close()


#-----------------------------------------------------------------------
# Cmdargs
#-----------------------------------------------------------------------

class CmdArgs:
    def __init__(self):
        parser = OptionParser()
        parser.add_option("--sql",dest="sql",default=None,
            help="sql statement to select field points,default is all sites")
        parser.add_option("--timelag",dest="timelag",default=60,
            help="allowable difference between image and field site dates")
        parser.add_option("--winsize",dest="winsize",default=3,
            help="size of window in number of landsat pixels")
        parser.add_option("--outfile",dest="outfile",default="out",
            help="name for output files. eg. output")
        parser.add_option("--analyse",dest="analyse",default=True,
            help="calculate stats on images")
        parser.add_option("--stage",dest="stage",
            help="required stage name eg. dbg, db3 or di7. At present these are the only options available",default='dbg')

        (options, args) = parser.parse_args()
        self.__dict__.update(options.__dict__)



#-----------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------

if __name__ == "__main__":

    cmdargs=CmdArgs()

    pointDict = {}

    print 'Script running. May take some time depending on number of images required.'

    points, headers = getFieldPoints(cmdargs.sql)

    for point in points:
        site = Observation(headers,point)
        pointDict[site.obs_key] = site

    print 'The following site visits do not have any Landsat scenes associated with them.'
    pointDict = searchDatabaseScenes(pointDict,cmdargs.timelag,cmdargs.stage[-2:],cmdargs.winsize)


    for statistic in ['mean','std']:
        if cmdargs.analyse is True:
            fileList=getFileList(pointDict,cmdargs.winsize)
            maskedFileList=applyMasks(fileList)
            print 'Calculating statistics...'
            pointDict = getStatistics(pointDict,cmdargs.winsize,statistic)


    output = cmdargs.outfile

    outCsv(pointDict,headers,output,cmdargs.analyse)



