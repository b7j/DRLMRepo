#!/usr/bin/env python
"""
Script to calculate the average distance from peak to trough in timetrace of npv cover 

"""
import argparse

from rios import applier

import pdb

import numpy as np

import time

#function to get cmd line inputs
def getCmdargs():
    p = argparse.ArgumentParser()
    p.add_argument("--imageList", help="input list of files")
    p.add_argument("--inDir", help="input directory")
    p.add_argument("--inROI", help ="input Region of interest .shp")
    p.add_argument("--outDir", help="output")
    cmdargs = p.parse_args()
    if cmdargs.imageList is None:
        p.print_help()
        sys.exit()

    return cmdargs



def main():
    """
    Main routine
    """
    cmdargs = getCmdargs()
    
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    controls = applier.ApplierControls()
    controls = applier.ApplierControls()
    controls.setOutputDriverName('GTiff')
    options = ['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES', 'INTERLEAVE=BAND', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256']
    controls.setCreationOptions(options)                                      
    controls.setWindowXsize(256) #set the rios block size to match the tiff tile size
    controls.setWindowYsize(256)
    
    allWinter, allAnnual, allSummer = doSeason(cmdargs.imageList, cmdargs.inDir)
    
    #pdb.set_trace()
    
    for i in allWinter:
	    
	    infiles.inimg = i
	    
	    year = i[0]
	    
	    year = year[-10:-6]
	    
	    outDirName = cmdargs.outDir + "winter"+ "_" + year +".tif"
    
    	    outfiles.comp = outDirName
       
            applier.apply(doAnalysis, infiles, outfiles, controls=controls)
	    
    
    for i in allSummer:
	    
	    infiles.inimg = i
	    
	    year = i[0]
	    
	    year = year[-10:-6]
	    
	    outDirName = cmdargs.outDir + "summer"+ "_" + year +".tif"
    
    	    outfiles.comp = outDirName
       
            applier.apply(doAnalysis, infiles, outfiles, controls=controls)
	    
    
    for i in allAnnual:
	    
	    infiles.inimg = i
	    
	    year = i[0]
	    
	    year = year[-10:-6]
	    
	    outDirName = cmdargs.outDir + "annual"+ "_" + year +".tif"
    
    	    outfiles.comp = outDirName
       
            applier.apply(doAnalysis, infiles, outfiles, controls=controls)
	
	
	    
	    
    
def doSeason(imageList,directory):
	
	years = []
	
	images = [line.strip() for line in open(imageList, 'r')]
		
	images.sort() # sort the filtered list on image date.
	
	#this gets the years out of the list of images
	for i in images:
		
		year = i[:-6]
		
		years.append(year)
		
	
	#this loops through the years one by one and creates a new list for each year with each season
		
	yearUnique = set(years)
	
	yearUnique = list(yearUnique)
	
	yearUnique.sort()
	
	allSummer = []
	
	allAnnual = []
	
	allWinter = []
	
	#pdb.set_trace()
	
	for i in range(len(yearUnique)):
				
		
		if i < len(yearUnique)-1:
			
			year1 = yearUnique[i]
		
			year2 = yearUnique[i+1]
							
			indexesY1 = [ii for ii,x in enumerate(years) if x == year1]
						
			matched1 = map(lambda j: images[j], indexesY1)
						
			indexesY2 = [ii for ii,x in enumerate(years) if x == year2]
						
			matched2 = map(lambda j: images[j], indexesY2)
			
			annual = matched1[3:]
							
			annual = [directory + s for s in annual]
			
			#pdb.set_trace()
			
			annual2 = matched2[:3]
			
			annual2 = [directory + s for s in annual2]
			
			annual.extend(annual2)
			
			allAnnual.append(annual)
			
			summer = matched1[10:]
			
			summer = [directory + s for s in summer]
			
			summer2 = matched2[:3]
			
			summer2 = [directory + s for s in summer2]
			
			summer.extend(summer2)
			
			allSummer.append(summer)
			
			winter = matched1[04:10]
			
			winter = [directory + s for s in winter]
			
			allWinter.append(winter)
					
		
			
				
	return allWinter, allAnnual, allSummer
	
	
	
	
# function to do the drill down through the image stack 
def doAnalysis(info, inputs, outputs):

    #pdb.set_trace()
    
    rain = np.array(inputs.inimg)
    
    rain = rain.astype(np.float)
    
    sumRain = np.sum(rain,axis=0)
    
    avgRain = np.mean(rain,axis=0)
    
    medRain = np.median(rain,axis=0)
    
    minRain = np.amin(rain,axis=0)
    
    maxRain = np.amax(rain,axis=0)
    
    stdRain = np.std(rain,axis=0)
    
    output = np.concatenate([sumRain,minRain,avgRain,medRain,maxRain,stdRain])
    
    outputs.comp = output #write to output array
   

 #Function to read in list of images to pass to applier   

 


if __name__ == "__main__":
    main()
