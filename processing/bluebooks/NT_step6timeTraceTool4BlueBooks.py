#!/usr/bin/env python
"""
Created on Wed Nov  6 12:26:37 2013

@author: Barnetson 

Loop to run stdmask and qv_rastbypoly.py

generates a list of statistics for imagery based on the polygon vector shapefile

Note: modified to include graphing function, works at this stage on only one polygon at a time, will code to include multiple polygons at another stage

Need to add a trend curve, tested with polyft and interpolate, needs more work, check this http://stackoverflow.com/questions/6939901/average-trend-curve-for-data-points-in-python

for a worked example


"""

# get all the imports
import sys
import os
import argparse
import glob
import csv
import qvf
import datetime
import numpy as np
import pdb
import math
import time

import qvf
from osgeo import gdal
from osgeo import osr
from osgeo.gdalconst import *
from rsc.utils import gdalcommon
import optparse
import pandas
import osr
import numpy.ma as ma
from collections import defaultdict

from numpy import *
import time
from commands import getoutput
import numpy.ma as ma
from scipy.stats import itemfreq
import string


#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--instage", help="Stage to process")

    p.add_argument("--imagelist", help="List of imagery to process")
    
    p.add_argument("--imagepath", help="Path to imagery")

    p.add_argument("--vector", help="Vector data for zonal stats, poly or point")

    p.add_argument("--uid", help="unique id field for zonal stats (id field must start with 1..)")

    p.add_argument("--csv", help="Name of output csv file")
    
    p.add_argument("--poly", help="poly or point input", default = False)
    
    p.add_argument("--latitude", help="if point vector, field name of latitude")
    
    p.add_argument("--longtitude", help="if point vector, field name of longtitude")
    
    p.add_argument("--window", help="Point window extract size", default = 3)
    
    p.add_argument("--ignore", default=0, type = int, help="Image background value to ignore (default = 0)")
    

    cmdargs = p.parse_args()
    
    if cmdargs.instage is None:

        p.print_help()

        sys.exit()

    return cmdargs



def convert_coord(image, geoX, geoY):
	
  #pdb.set_trace()	
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
  
  #pdb.set_trace()
  
  pix = gdalcommon.wld2pix(geotransform, geoX, geoY)
  
  offset = math.floor(window/2)  
   
  if (0<(pix.x-offset)<ds.RasterXSize) and (0<(pix.y-offset)<ds.RasterYSize) and (0<(pix.x+offset)<ds.RasterXSize) and (0<(pix.y+offset)<ds.RasterYSize):
    return ds.ReadAsArray(int(pix.x-offset), int(pix.y-offset), window, window)
  else:
    return array(ignore)

#function to export data
def exportData(data,outputName):

    w = csv.writer(file(outputName, 'wb'), dialect = 'excel') #create csv file

    w.writerows(data) #write to file
  
def pointExtract(filelist,df,window,ignore):
	
	
    outputlist = []

    counter = 0 # image counter
    
    # this bit filters out multiple transects per site
    
    geoY = []
    
    geoX = []
    
    dates = []
    
    siteId = []
    
    #propertys = []
    
    fieldBare = []
    
    fieldNPV = []
    
    fieldPV = []
    
    for name, group in df.groupby(['date','siteId','lat','longt','totalBareCover','totalNPVCover','totalPVCover']):
	    
       		#pdb.set_trace()
		
		geoY.append(name[2])
	    
    		geoX.append(name[3])
	    
    		dates.append(name[0])
		
		siteId.append(name[1])
				
		#propertys.append(name[4])
		
		fieldBare.append(name[4])
		
		fieldNPV.append(name[5])
		
		fieldPV.append(name[6])
    
    newDict = defaultdict(list)
       
    # loop through the stack of images	

    for filename in filelist: 

        counter += 1 # add one to the counter
	
	#filename = filelist[70]
	
	t = time.time()

	
        print str(counter) + ' of ' + str(len(filelist)) # print the counter 
	
	        
        imagename = filename[-34:] 

        season = filename[-22:-10]
	
	
		
	for i in range(len(geoX)):
				
		lat = float(geoX[i])
		
		longt = float(geoY[i])
		
		site = siteId[i]
		
		date = dates[i]
		
		#property = propertys[i]
		
		fB = fieldBare[i]
		
		fNPV = fieldNPV[i]
		
		fPV = fieldPV[i]
		#pdb.set_trace()
		
		east, north = convert_coord(filename, lat, longt)
					
		stack = extract_window(filename, east, north, window, ignore)
	
		zeroTest = stack.sum()
	
		stats = []
		
		#pdb.set_trace()
				
		if zeroTest == 0:
			
			#pdb.set_trace()
			
			for n in range(6):
				
				stats.append('-999')
				
			noPixels = str(9)
			
					
		else:
			
			b1 = ma.masked_values(stack[0],0)
			
			b1m = b1.mean()
			
			stats.append(str((b1m)-100))
			
			b2 = ma.masked_values(stack[1],0)
			
			b2m = b2.mean()
			
			stats.append(str((b2m)-100))
			
			b3 = ma.masked_values(stack[2],0)
			
			b3m = b3.mean()
			
			stats.append(str((b3m)-100))
				
			b1 = ma.masked_values(stack[0],0)
					
			b1m = b1.std()
			
			stats.append(str(b1m))
			
			b2 = ma.masked_values(stack[1],0)
			
			b2m = b2.std()
			
			stats.append(str(b2m))
			
			b3 = ma.masked_values(stack[2],0)
			
			b3m = b3.std()
			
			stats.append(str(b3m))
			
			noPixels = str((stack[0]== 0).sum())
			
			statsOut = ",".join(stats)
			
			newDict['numberPixels'].append(noPixels)
					
			newDict['stats'].append(statsOut)
				
			newDict['lat'].append(lat)
				
			newDict['longt'].append(longt)
				
			newDict['date'].append(date)
				
			newDict['siteId'].append(site)
				
			#newDict['property'].append(property)
				
			newDict['imageName'].append(imagename)
				
			newDict['season'].append(season)
			
			newDict['fieldBare'].append(fB)
			
			newDict['fieldNPV'].append(fNPV)
			
			newDict['fieldPV'].append(fPV)
	
	# do stuff
	elapsed = time.time() - t
		
	print str(elapsed)
		
	#pdb.set_trace()
		
                
		
    	
	
    return newDict  
  


#main function
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    imagelist = cmdargs.imagelist #get the image path from the get cmd
    
    #pdb.set_trace()
    
    filelist = []
    
    with open(imagelist, "r") as ifile:
	
	for line in ifile:
		
		#pdb.set_trace()
		
		lineA = line.rstrip()
		
		lineB = lineA.strip('\n')
		
		path = cmdargs.imagepath + lineB
		
		filelist.append(path)
		
		
	

    #pdb.set_trace()
    
    filelist.sort(key=lambda x: x.split("_", 2)[-1]) # sort the filtered list on image date.

    df = pandas.read_csv(cmdargs.vector,header=0)
	    	    
    #pdb.set_trace()
	    
    window = int(cmdargs.window)
	    
    ignore = float(cmdargs.ignore)
	    
    output = pointExtract(filelist,df,window,ignore)

    #pdb.set_trace()
    
    fileName = cmdargs.csv
    
    df = pandas.DataFrame(output)
    
    df.to_csv(fileName)
    
    #exportData(outputlist,cmdargs.csv)#write data out to a excel csv file

        
if __name__ == "__main__":
    mainRoutine()