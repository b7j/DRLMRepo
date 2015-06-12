#!/usr/bin/env python

'''

Creates a list of coincedental images to ausplots field data

'''

import sys
import qvf
from numpy import *
from osgeo import gdal
from osgeo import osr
from osgeo.gdalconst import *
from rsc.utils import gdalcommon
import optparse

from xlrd import open_workbook
import argparse
import pdb
import csv
import datetime
import xlrd
import time
import numpy as np
import os
from commands import getoutput


#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()
    
    p.add_argument("--inputcsv", help="Input csv file containing site details")

    p.add_argument("--out", help="Name of output text file")
    
    p.add_argument("--ignore", default=0, type = int, help="Image background value to ignore (default = 0)")
    
    p.add_argument("--window", default=3, type = int, help="Dimension of square window (default = 3)")

    cmdargs = p.parse_args()
    
      
    if cmdargs.inputcsv is None:

        p.print_help()

        sys.exit()

    return cmdargs


#function to export data
def exportData(data,outputName):

    f = open(outputName,'wt')

    for item in data:

        f.write(item + '\n')

    f.close()
    

    #w = csv.writer(file(outputName, 'wb'), dialect = 'excel',delimiter=',') #create csv file

    #w.writerows(data) #write to file
 

#function to get siteids and assocaited object ids used in timetrace processn
def getSiteDetails(infile):

    reader = csv.reader(infile) # read the temp csv file

    dates = []

    dateTuple = []

    pathRow = []

    siteId = []
    
    fieldId = []
    
    lat = []
    
    longt = []
    
    for rows in reader:

        fieldDate = rows[2]
		
        day = fieldDate[:2]
	
	day = day.strip('/')
	
	day = int(day)

        month = fieldDate[2:5]
	
	month = month.strip('/')
	
	month = int(month)
	
	print month

        year = int(fieldDate[6:])
	
	#pdb.set_trace()

        date = datetime.datetime(year,month,day)

        a = time.mktime(date.timetuple()) 

        dates.append(fieldDate)

        dateTuple.append(a)

        siteId.append(rows[3])

        pathRow.append(rows[4])
	
	fieldId.append(rows[5])
	
	lat .append(rows[0])
	
	longt.append(rows[1])

    infile.close()

    return dates, siteId, pathRow, dateTuple, fieldId, lat, longt


## Function to convert coordinate from lat/long to image projection
def convert_coord(image, geoX, geoY):
  ds = gdal.Open(image, GA_ReadOnly)
  badWKT = ds.GetProjection()
  dsWKT = gdalcommon.fixDodgyImagineSpheroid(badWKT)
  dsProj = osr.SpatialReference(dsWKT)
  pWKT = 'GEOGCS["WGS_1984",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.2572235629972],TOWGS84[0,0,0,0,0,0,0]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'    
  pProj = osr.SpatialReference(pWKT)
  ct = osr.CoordinateTransformation(pProj, dsProj)
  (easting, northing, z) = ct.TransformPoint(geoX,geoY)
  return (easting, northing)


## Function to extract pixel window
def extract_window(image, geoX, geoY, window, ignore):
  ds = gdal.Open(image, GA_ReadOnly)
  geotransform = ds.GetGeoTransform()
  pix = gdalcommon.wld2pix(geotransform, geoX, geoY)
  offset = floor(window/2)   
  if (0<(pix.x-offset)<ds.RasterXSize) and (0<(pix.y-offset)<ds.RasterYSize) and (0<(pix.x+offset)<ds.RasterXSize) and (0<(pix.y+offset)<ds.RasterYSize):
    return ds.ReadAsArray(int(pix.x-offset), int(pix.y-offset), window, window)
  else:
    return array(ignore)




def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    infile = open(cmdargs.inputcsv, "rb")
    
    [date, siteId, pathRow, dateTuple, fieldIds, lat, longt] = getSiteDetails(infile)

    finalList = []

    #pdb.set_trace()

    for i in range(len(date)):

        site = siteId[i]
	
	siteDate = date[i]
	
	sitePathRow = pathRow[i]
	
	siteFieldIds = fieldIds[i]
	
	siteLat = lat[i]
	
	siteLong = longt[i]
	
	year = date[i]

        year = '20' + year[-2:]

        wrs = pathRow[i]
	
	wrs = wrs[0:3] + '_' + wrs[3:]

        cmd = "find /apollo/imagery/rsc/landsat/landsat57tm/wrs2/" + wrs + "/" + year + "/ " + "-name '*dil*'"
        
        output = getoutput(cmd)

        #pdb.set_trace()

        outputList = output.splitlines()
	
	

        fieldDate = dateTuple[i]

        imageDates = []
	
	

        #loop to get out image dates

        for index in range(len(outputList)):

            a = outputList[index]

            #pdb.set_trace()

            b = a[-18:-10]

            day = int(b[-2:])

            month = int(b[-4:-2])

            year = int(b[:-4])

            #dateA = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:00"

            dateA = datetime.datetime(year,month,day)

            a = time.mktime(dateA.timetuple()) 

            imageDates.append(a)


        #lets do some matching to find the closest image date to that of the field date.
	
	plusMonth = fieldDate + 2592000
	
	minusMonth = fieldDate - 2592000

        match1 = min(range(len(imageDates)),key=lambda ii: abs(imageDates[ii]-fieldDate))
		
	match2 = min(range(len(imageDates)),key=lambda ii: abs(imageDates[ii]-plusMonth))
	
	match3 = min(range(len(imageDates)),key=lambda ii: abs(imageDates[ii]-minusMonth))
	
	
	
	'''
        matchedDate = imageDates[match]

        difference = matchedDate - fieldDate


        pdb.set_trace()

        if difference <0:

            difference = abs(difference)

            #exclude sites older than one month wich is 2592000 seconds

        if difference < 2592000:

             #pdb.set_trace()
      
             d = outputList[match]
	 '''
	d = outputList[match1]
	
	pdb.set_trace()
	
	(easting, northing) = convert_coord(d[-34:], siteLong, siteLat)
        
        #Extract image window
        stack = extract_window(d[-34:], easting, northing, cmdargs.window, cmdargs.ignore)
		
        finalList.append(d[-34:] + ',' + site + ',' + siteDate + ',' + sitePathRow + ',' + siteFieldIds + ',' + siteLat + ',' + siteLong)
	
	d = outputList[match2]
		
        finalList.append(d[-34:] + ',' + site + ',' + siteDate + ',' + sitePathRow + ',' + siteFieldIds + ',' + siteLat + ',' + siteLong)
	
	d = outputList[match3]
		
        finalList.append(d[-34:] + ',' + site + ',' + siteDate + ',' + sitePathRow + ',' + siteFieldIds + ',' + siteLat + ',' + siteLong)
	
  
  	
    #pdb.set_trace()

   
    
    
    exportData(finalList,cmdargs.out)#write data out to a excel

    print 'stop'








if __name__ == "__main__":
    mainRoutine()