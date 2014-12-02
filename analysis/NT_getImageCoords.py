# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 13:08:49 2013

@author: barnetj

little bit of python to get average pixel values around a known coordinate for the purposes of validation
"""
#import all the dependencies

import osgeo.gdal

from osgeo import gdal, gdalnumeric, ogr, osr

import numpy as np

import os

output = open('/export/home/barnetj/ValidationSummary.txt', "w")

#method to get geomatrix info
def coord2pixel(geoMatrix, x, y):
    
   
    ulX = geoMatrix[0]

    ulY = geoMatrix[3]

    xDist = geoMatrix[1]

    yDist = geoMatrix[5]

    rtnX = geoMatrix[2]

    rtnY = geoMatrix[4]

    pixel = np.round((x - ulX) / xDist).astype(np.int)

    line = np.round((ulY - y) / xDist).astype(np.int)

    return (pixel, line)

# get file directory details

imagePath = '/export/home/barnetj/validation/'

coordFile = '/export/home/barnetj/validation/coords2.txt'

#import the list of coords,!!ensure coords are in the same zone as the image!!

coordData = []

with open(coordFile, 'ru') as f:
    
    for line in f:
        
        line = line.strip()
        
        line = line.split(',')
        
        coordData.append(line)
        
#get the list of images

imageDir = os.listdir(imagePath)

list.sort(imageDir)



for files in imageDir:
    
    if files.endswith(".img"):
    
        image = imagePath + files
        
        
        # Open the image as a read only image
        
        ds = osgeo.gdal.Open(image,gdal.GA_ReadOnly)
        
        # Check the ds (=dataset) has been successfully open
        
        # otherwise exit the script with an error message.
        
        if ds is None:
        
            raise SystemExit("The raster could not openned")
        
        # get the georeferencing information from the image
                
        geoMatrix = ds.GetGeoTransform()
        
        #get the easting and northings from the coordData list    
        
        for line in coordData:
            
            easting = float(line[2])
            
            northing = float(line[3])
            
             #open the image into an array
                
            srcArray = gdalnumeric.LoadFile(image)
            
            # test if coordinates are within image bounds
            
            arraySize = srcArray.shape
            
            rows = arraySize[1]
            
            cols = arraySize[2]
            
            right = cols*30 + geoMatrix[0]
            
            left = geoMatrix[0]
            
            top = geoMatrix[3]
                        
            bottom = geoMatrix[3] - rows*30
            
            if easting >left and easting <right:            
            
                xRange = 1
                
            else: 
                
                xRange = 0
                
            if northing >bottom and northing <top:
                
                yRange = 1
                
            else:
            
                yRange = 0
                
            rangeTest = xRange + yRange
            
            if rangeTest == 2:
                                   
                # get the image coordinates 
                
                imageX, imageY = coord2pixel(geoMatrix, easting, northing)
                               
                    
                #apply the mask surrounding the pixel
                         
                                
                numBands = len(arraySize)
                
                
                # test if multiband image ie frac cover or single band ie fpc    
                if numBands >2:
                    
                    focal = np.zeros((5,3,3))
                     
                    focal[:,1,1] = srcArray[:,imageY, imageX]
                        
                    focal[:,0,0] = srcArray[:,imageY-1, imageX-1]
                        
                    focal[:,0,1] = srcArray[:,imageY-1, imageX]
                        
                    focal[:,0,2] = srcArray[:,imageY-1, imageX+1]
                        
                    focal[:,1,0] = srcArray[:,imageY, imageX-1]
                        
                    focal[:,1,2] = srcArray[:,imageY, imageX+1]
                        
                    focal[:,2,0] = srcArray[:,imageY+1, imageX-1]
                        
                    focal[:,2,1] = srcArray[:,imageY+1, imageX]
                        
                    focal[:,2,2] = srcArray[:,imageY+1, imageX+1]
                        
                    b1avg = np.mean(focal[0,:,:])
                        
                    b2avg = np.mean(focal[1,:,:])
                        
                    b3avg = np.mean(focal[2,:,:])
                        
                    b4avg = np.mean(focal[3,:,:])
                        
                    b5avg = np.mean(focal[4,:,:])
                    
                    out = 'Date,' + line[0] + ',siteID,' + line[1] + ',Easting,' + line[2] + ',Northing,' + line[3] + ',ImageName,' + files + ',FieldBare,' + line[4] + ',FieldBrown,'\
                    + line[5] + ',FieldGreen,' + line[6] + ',FieldFPC,' + line[7] + ',ImageBare,' + str(b1avg) + ',ImageGreen,' + str(b2avg) + ',ImageNonGreen,' + str(b3avg) + "\n"
                    
                elif numBands == 1:
                        
                    focal = np.zeros((3,3))
                            
                    focal[1,1] = srcArray[imageY, imageX]
                        
                    focal[0,0] = srcArray[imageY-1, imageX-1]
                        
                    focal[0,1] = srcArray[imageY-1, imageX]
                        
                    focal[0,2] = srcArray[imageY-1, imageX+1]
                        
                    focal[1,0] = srcArray[imageY, imageX-1]
                        
                    focal[1,2] = srcArray[imageY, imageX+1]
                        
                    focal[2,0] = srcArray[imageY+1, imageX-1]
                        
                    focal[2,1] = srcArray[imageY+1, imageX]
                        
                    focal[2,2] = srcArray[imageY+1, imageX+1]
                        
                    b1avg = np.mean(focal[:,:])
                
                    out = 'FieldDate,' + line[0] + ',SiteID,' + line[1] + ',Easting,' + line[2] + ',Northing,' + line[3] + ',ImageName,' + files +  ',FieldFPC,' + line[7] + ',ImageFPC,' + str(b1avg)
    
                output.write(out)

close(output)