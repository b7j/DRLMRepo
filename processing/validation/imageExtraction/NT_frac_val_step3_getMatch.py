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
import collections


#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()
    
    p.add_argument("--inputcsv", help="Input csv file from intersect of the output from step 2")

    p.add_argument("--out", help="Name of output csv file")
   
    p.add_argument("--imageList", help = "image list of existing imagery pulled down")

    cmdargs = p.parse_args()
    
      
    if cmdargs.inputcsv is None:

        p.print_help()

        sys.exit()

    return cmdargs



def sendToOutput(myDict,fileName):

        with open(fileName, 'w') as f:
	
		writer = csv.writer(f)  
		  
		for k,v in myDict.iteritems():
			
			writer.writerow([k] + v)               
		       

#function to export data
def exportData(data,outputName):

    f = open(outputName,'wt')
    
    #pdb.set_trace()

    for item in data:
	    
	    if item is not None:
		    
	    
		for i in item:
			
			f.write(i + '\n')

    f.close()
    

    #w = csv.writer(file(outputName, 'wb'), dialect = 'excel',delimiter=',') #create csv file

    #w.writerows(data) #write to file
  
def getCsvData(fileName):
	    
	#pdb.set_trace()    
        with open(fileName, 'r') as f:
		
		reader = csv.reader(f)    
		
		mydict = collections.defaultdict(list)
		
		for row in reader:
			
			mydict[row[0]] = row[1:]
			
	return mydict		
			
	    
    
#function to get siteids and assocaited object ids used in timetrace processn



def getImageList(filename):
	
	
    imageList = filename #get the image path from the get cmd
    
    filelist = []
    
    with open(imageList, "r") as ifile:
	
	for line in ifile:
		
		#pdb.set_trace()
		
		lineA = line.rstrip()
		
		lineB = lineA.strip('\n')
		
		filelist.append(lineB)
		
		
    return filelist 	

def doMatching(imageDates,fieldDate):
	
	 match = min(range(len(imageDates)),key=lambda ii: abs(imageDates[ii]-fieldDate))
	 
	 return match


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

	
def searchFileStore(fieldDate,pathRow):
				
	#get list of images from filestore
	
	#pdb.set_trace()
	
	fieldDate = xlrd.xldate.xldate_as_tuple(fieldDate,0)
	
    	year = str(fieldDate[0])

        wrs = pathRow[0:3] + '_' + pathRow[-3:]

        cmd = "find /apollo/imagery/rsc/landsat/landsat57tm/wrs2/" + wrs + "/" + year + "/ " + "-name '*dc4*'"
        
        output = getoutput(cmd)

        #pdb.set_trace()

        outputList = output.splitlines()

        fieldDateTuple = fieldDate

        imageDates = []
	
	outputImages = []

        #loop to get out image dates

        for index in range(len(outputList)):

            a = outputList[index]
	    
	    im = a[-34:]
	    
	                
            b = a[-18:-10]

            day = int(b[-2:])

            month = int(b[-4:-2])

            year = int(b[:-4])

            #dateA = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:00"

            dateA = datetime.datetime(year,month,day)

            	    	    
	    temp = datetime.datetime(1899, 12, 31)
    	    
	    delta = dateA - temp
          
	    out = float(delta.days) + (float(delta.seconds) / 86400)

            #pdb.set_trace()
	    
	    imageDates.append(out)
	    
	    outputImages.append(im)

			
		
	return imageDates, outputImages		
						
def existingImages(imageList, pathRow):
	
	#loop to find matching path rows
	imagesMasked = []
	
	images = []
	
	for ii in imageList:
	
		p = ii[8:11]
		
		r = ii[12:15]
		
		pR = p+r
		
		
		if pathRow == pR:
			
			image = ii[0:-14] + '.img'
			
			images.append(image)
			
			imagesMasked.append(ii)
		
	#pdb.set_trace()	
	
	#loop to get out image dates
	
	imageDates = []

        for index in imagesMasked:

            b = index[-28:-20]

            day = int(b[-2:])

            month = int(b[-4:-2])

            year = int(b[:-4])

            #dateA = str(year) + "-" + str(month) + "-" + str(day) + " 00:00:00"
	
	    #pdb.set_trace()
	
            dateA = datetime.datetime(year,month,day)
	    	    	    
	    temp = datetime.datetime(1899, 12, 31)
    	    
	    delta = dateA - temp
          
	    out = float(delta.days) + (float(delta.seconds) / 86400)

            imageDates.append(out)
	    
	return imageDates,images, imagesMasked
	
def offsetMatching(offsetDates,imageDates,images):
	
	output = []
		
	for it in offsetDates:
		
		match = doMatching(imageDates,it)
		
		#pdb.set_trace()		
	
		d = images[match]
		
		imDate = imageDates[match]
	
		#im = cmdargs.inputDir + d
			
		output.append(d)
			
	return output
		
def compareExisting(filestoreIms,existingIms):
			
	#pdb.set_trace()		
			
	a = list(set(filestoreIms) - set(existingIms))
	
	missing = []
		
	if len(a) > 0:
			
		return a
		
		
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    #pdb.set_trace()

    #result = siteDetailsDictionary(cmdargs.inputcsv)
    
    fileName = cmdargs.inputcsv
    
    result = getCsvData(fileName)
    
                    
    date = result['date']
            
    #pdb.set_trace()	    
	    
    dateTuple = date
    
    pathRow =result['WRSPR']
    
    missingList = []
         
    existingList = []

    #Loop through sites
    #pdb.set_trace()

    for i in range(len(date)):
	    
		
	print str(i)
	
	values = []
    
    	'''
    	#loop to get all the values out of the dictionary per site
	for key, value in result.iteritems():
	    
	    values.append(value[i])
	    
	outList = ",".join(values)
	
	'''

       	siteDate = date[i]
	
	sitePathRow = pathRow[i]
	
	fieldDate = int(dateTuple[i])
	
	imageList = getImageList(cmdargs.imageList)
	
	
        existingImDates, images, imagesMasked = existingImages(imageList, sitePathRow)
	
	fileStoreImDates, fileStoreImages = searchFileStore(fieldDate,sitePathRow)
        	

	

        #lets do some matching to find the closest image date to that of the field date.
	
	plusMonth = fieldDate + 30 # fix this to be offset of excel dates
	
	minusMonth = fieldDate - 30
	
	offsetDates = [fieldDate,plusMonth,minusMonth]
	
	existingImsNoMask = offsetMatching(offsetDates,existingImDates,images)
	
	existingImsMasked = offsetMatching(offsetDates,existingImDates,imagesMasked)
	
	fileStoreIms = offsetMatching(offsetDates,fileStoreImDates,fileStoreImages)		
				
	#pdb.set_trace()
	
	missing = compareExisting(fileStoreIms,existingImsNoMask)
				
	missingList.append(missing)
					
	existingList.append(existingImsMasked)
		
	k1 = 'existingImages'
	
	k2 = 'missingImages'
	
	#pdb.set_trace()
	
	result.setdefault(k1, [])
		    	    
	result[k1].append(existingImsMasked)
	
	result.setdefault(k2, [])
		    	    
	result[k2].append(missing)
	
		
        
    outName1 = 'missing_' + cmdargs.out + '.txt'
    
    outName2 = 'exisiting_' + cmdargs.out + '.txt'
    
    outName3 = 'matched_' + cmdargs.out + '.csv'
    
    exportData(missingList,outName1)
    
    exportData(existingList,outName2)
    
    sendToOutput(result,outName3)
    
    

    print 'stop'








if __name__ == "__main__":
    mainRoutine()