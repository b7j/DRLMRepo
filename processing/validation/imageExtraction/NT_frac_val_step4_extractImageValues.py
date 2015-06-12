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
import numpy.ma as ma
from scipy.stats import itemfreq


#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()
    
    p.add_argument("--inputcsv", help="Input csv file containing site details")

    p.add_argument("--out", help="Name of output csv file")
    
    p.add_argument("--ignore", default=0, type = int, help="Image background value to ignore (default = 0)")
    
    p.add_argument("--window", default=3, type = int, help="Dimension of square window (default = 3)")
    
    #p.add_argument("--instage", help = "input stage")
    
    p.add_argument("--inputDir", help = "directory to image")
    
  

    cmdargs = p.parse_args()
    
      
    if cmdargs.inputcsv is None:

        p.print_help()

        sys.exit()

    return cmdargs


#function to export data
def exportData(data,header,outputName):

    f = open(outputName,'wt')
    
    counter = 0
    
    #pdb.set_trace()

    for item in data:
	    
	counter += 1
	
	if counter == 1:
		
		f.write(header + '\n')

        f.write(item + '\n')

    f.close()
    

    #w = csv.writer(file(outputName, 'wb'), dialect = 'excel',delimiter=',') #create csv file

    #w.writerows(data) #write to file
 
def siteDetailsDictionary(filename):
	
	#pdb.set_trace()
	
	
	reader = csv.DictReader(open(filename))

	result = {}
	
	for row in reader:
		
		for column, value in row.iteritems():
			
			result.setdefault(column, []).append(value)
		
	return result

#function to get siteids and assocaited object ids used in timetrace processn


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

def getDateTuple(dates):
	
	dateTuple = []
	
	for date in dates:
			
		day = date[:2]
		
		day = day.strip('/')
			
		day = int(day)
		
		month = date[2:5]
			
		month = month.strip('/')
			
		month = int(month)
		
		year = int(date[6:])
	
		#pdb.set_trace()

        	date = datetime.datetime(year,month,day)

        	a = time.mktime(date.timetuple()) 

		
		dateTuple.append(a)
		
	return dateTuple

	
def doImageExtraction(im,siteLat,siteLong,window,ignore,imDate,fieldDate):
			
	#pdb.set_trace()
	
	(easting, northing) = convert_coord(im, float(siteLong), float(siteLat))
        
        #Extract image window
        stack = extract_window(im, easting, northing,window, ignore)
	
	zeroTest = stack.sum()
	
	stats = []
	
	#pdb.set_trace()
			
	if zeroTest == 0:
		
		for n in range(6):
			
			stats.append('-999')
			
		noPixels = str((stack[0]== 0).sum())
		
				
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
	
	#pdb.set_trace()
	
	diff = str((imDate-int(fieldDate)))
	
	#pdb.set_trace()
	
	sensor = im[-44:-42]
	
	imName = im[-44:]
	
	year = im[-28:-24]
			
	return statsOut,diff,noPixels,sensor,year				
						
def doStripping(inputs):
	
	#pdb.set_trace()
	
	a = inputs.strip('[')
							
	a = a.strip(']')
							
	a = a.strip(" ")
	
	a = a.strip("'")
	
	
	return a
	
def getImDate(imName):
	
	#pdb.set_trace()
	
	b = imName[-28:-20]

        day = int(b[-2:])

        month = int(b[-4:-2])

        year = int(b[:-4])

        dateA = datetime.datetime(year,month,day)
	    	    	    
	temp = datetime.datetime(1899, 12, 31)
    	    
	delta = dateA - temp
          
	out = float(delta.days) + (float(delta.seconds) / 86400)
	
	return out

def recallImages(imName,destDir):
	
	#pdb.set_trace()
	
	cmd = 'qv_recall_to_pc ' + imName + ' --destdir ' + destDir
					
	os.system(cmd) #call it
	
def masking(image,outDir):
	
	#pdb.set_trace()
	
	stdmasked = qvf.changeoptionfield(image, 'z', 'stdmasks') # changesone of the options in the standard 
	
	im = outDir + image
	
	std = outDir + stdmasked
	
	cmd = "qv_applystdmasks.py --infile %s --outfile %s" % (im, std) # call the standard mask
        
        os.system(cmd) #call it
		
	return std	

def appendDict(inDict,value,key):
	
						
	inDict.setdefault(key, [])
		    	    
	inDict[key].append(value)
	
	return inDict
	

def sendToOutput(myDict,fileName):

        with open(fileName, 'w') as f:
	
		writer = csv.writer(f)  
		  
		for k,v in myDict.iteritems():
			
			writer.writerow([k] + v)               
		       
	

def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    

    result = siteDetailsDictionary(cmdargs.inputcsv)
    
    keys = result.keys()

    missing = result['missingImages']
    
    existing = result['existingImages']
    
    lat = result['lat']
    
    longt = result['long']
    
    date = result['date']
    
    finalList = []
    
    vals = result.values()

    newDict = {}
    #Loop through sites
    
    
    
    noSites = len(lat)
    
    #pdb.set_trace()

    for i in range(noSites):
	    
		
	print str(i)
			
	siteLat = lat[i]
	
	siteLong = longt[i]
	
	fieldDate = date[i]
			
	pdb.set_trace()		
		
	imageMissing = missing[i]
	
	imageExisting = existing[i]
	
	imageExisting = imageExisting.split(',')
	
	if len(imageMissing) >0:
		
		images = imageMissing.split(',')
			
		if len(images) > 1:
			
			for iii in images:
				
				imageExisting.append(iii)
							
	for z in range(len(imageExisting)):
		
		
		#pdb.set_trace()
								
		a = doStripping(imageExisting[z])
		
		if len(a) > 0:
		
			imNameOutput = a
					
			#pdb.set_trace()
							
			destDir = cmdargs.inputDir		
							
			if len(a) == 34:
					
				recallImages(a,destDir)
							
				stdMask = masking(a,destDir)
				
				imDate = getImDate(stdMask)
			
			else:
				
				stdMask = destDir + a
			
				imDate = getImDate(stdMask)
			
			statsOut,diff,noPixels,sensor,year = doImageExtraction(stdMask,siteLat,siteLong,cmdargs.window, cmdargs.ignore,imDate,fieldDate)		
					
			#pdb.set_trace()		
					
			data = []		
					
			for k in range(len(keys)):		
						
				a = vals[k]
				
				b = a[i]
				
				if b is None:
					
					b = 'NaN'
				
				data.append(b)
					
			newVals = [diff,noPixels,sensor,year,imNameOutput]
			
			stats = statsOut.split(',')
			
			for s in stats:
				
				newVals.append(s)
			
					
			newKeys = []
			
			imKey = ['diff','noPixels','sensor','year','imName','b1','b2','b3','b1s','b2s','b3s']
			
			for d in data:
			
				newVals.append(d)
				
			for d in imKey:
				
				newKeys.append(d)	
				
			for d in keys:
				
				newKeys.append(d)
					
			#pdb.set_trace()
					
			for dd in range(len(newKeys)):
				
				newDict.setdefault(newKeys[dd], [])
				
				newDict[newKeys[dd]].append(newVals[dd])
			
			#pdb.set_trace()
    fileName = cmdargs.out
		
    sendToOutput(newDict,fileName)		







if __name__ == "__main__":
    mainRoutine()