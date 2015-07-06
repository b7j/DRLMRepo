#!/usr/bin/env python
import pdb

import os

import argparse

import csv

from osgeo import ogr

import numpy as np

import collections






#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--imageList", help="Input image")
    
    p.add_argument("--imageDir", help="Input image directory")

    p.add_argument("--inputVector", help="Input shapefile of area to be analysed")

    p.add_argument("--uid", help="Shapefile unique ID")
    
    p.add_argument("--tempDir", help="temp directory")

    p.add_argument("--outputfile", help = "output text file")

    p.add_argument("--fieldName", help = "field name in shapefile with feature names for plotting")
    



    cmdargs = p.parse_args()
    
    if cmdargs.imageList is None:

        p.print_help()

        sys.exit()

    return cmdargs
 


# Set up the function to be applied
def doCounts(imageList,vec,uid,tempDir,imageDir):
   
   

    allCounts = []
    
    images = [line.strip() for line in open(imageList, 'r')]
		
    images.sort() # sort the filtered list on image date.

    bigDict = {}
    
    bigDict.setdefault('avg', [])
	
    bigDict.setdefault('id', [])
    
    bigDict.setdefault('year', [])
    
    bigDict.setdefault('season', [])

    #pdb.set_trace()

    for i in images: 
	    
	print i

	image = imageDir + i
	
	year = i[-8:-4]
	
	season = i[:-9]
	
	#pdb.set_trace()

        csvfile = tempDir + "temp.csv"

        cmd = "qv_rastbypoly.py -r %s -v %s -c %s -o %s --stats mean" % (image, vec, uid, csvfile)

        os.system(cmd)
	
	
	
	data = getCsvData(csvfile)
	
	values = data.values()
	
	keys = data.keys()
    
    	values = np.array(values)
	
	
	
	for n in range(len(values)):
		
	    item = values[n]
	            
	    	    
	    bigDict['avg'].append(float(item[2]))
	    
	    bigDict['id'].append(float(keys[n]))
	    
	    bigDict['year'].append(int(year))
	    
	    bigDict['season'].append(season)
	    
    	#pdb.set_trace()
	    
    return bigDict
	
        #pdb.set_trace()
	 
           
def getCsvData(fileName):
	    
	    
        with open(fileName, 'r') as f:
		
		reader = csv.reader(f)    
		
		mydict = collections.defaultdict(list)
		
		for row in reader:
			
			#pdb.set_trace()
			
			mydict[row[0]] = row[1:]
			
	return mydict


def doRegionAnalysis(results):
	
	#pdb.set_trace()
	
	#longterm seasonal analysis
	
	season = results['season']
	
	seasonList = set(season)
	
	ids = results['id']
	
	avg = results['avg']
	
	year = results['year']
	
	newDict = {}
	
	newDict.setdefault('id', [])
	
	newDict.setdefault('season', [])
	
	newDict.setdefault('longterm_avg', [])
	
	newDict.setdefault('longterm_lower', [])
	
	newDict.setdefault('longterm_mid', [])
	
	newDict.setdefault('longterm_upper', [])
	
	newDict.setdefault('longterm_median', [])
	
	newDict.setdefault('current_avg', [])
	
	newDict.setdefault('seasonalityScore', [])
	
	#pdb.set_trace()
	
	for s in seasonList:
				
		print s
		
		#this gets all the components for a particular season
				
		index = [ii for ii,x in enumerate(season) if x == s]
		
		matchedId = map(lambda j: ids[j], index)
		
		matchedAvgs = map(lambda j: avg[j], index)
		
		matchedYears = map(lambda j: year[j], index)
		
		#pdb.set_trace()
		
		
		idSet =set(matchedId)
		
		for i in idSet:
			
			ind = [ii for ii,x in enumerate(matchedId) if x == i]
				
			#pdb.set_trace()
			
			regionAvgs = map(lambda j: matchedAvgs[j], ind)
			
			regionYears = map(lambda j: matchedYears[j], ind)
			
			m = max(regionYears)
			
			yearIndex = [ii for ii,j in enumerate(regionYears) if j == m]
			
			yearIndex = int(yearIndex[0])
			
			currentAvg = regionAvgs[yearIndex]
			
			
			longterm = np.array(regionAvgs)
			
			#pdb.set_trace()	
								
			newDict['id'].append(i)
			
			newDict['season'].append(s)
			
			newDict['current_avg'].append(currentAvg)
						
			newDict['longterm_avg'].append(np.mean(longterm))
			
			newDict['longterm_median'].append(np.median(longterm))
			
			lower = np.percentile(longterm,33.333,axis=0)
			
			newDict['longterm_lower'].append(lower)
			
			mid = np.percentile(longterm,66.666,axis=0)
			
			newDict['longterm_mid'].append(mid)
			
			upper = np.percentile(longterm,99.999,axis=0)
						
			newDict['longterm_upper'].append(upper)
			
			
			
			if currentAvg > mid:
				
				newDict['seasonalityScore'].append(3)
				
			elif currentAvg < mid and currentAvg > lower:
				
				newDict['seasonalityScore'].append(2)
				
			elif currentAvg < lower:
				
				newDict['seasonalityScore'].append(1)
				
					
					
	#pdb.set_trace()		
		
		
		
	return newDict
	

def sendToOutput(myDict,fileName):

        with open(fileName, 'w') as f:
	
		writer = csv.writer(f)  
		  
		for k,v in myDict.iteritems():
			
			writer.writerow([k] + v)        


def main():

    cmdargs = getCmdargs() # instantiate the get command line function

    results = doCounts(cmdargs.imageList, cmdargs.inputVector, cmdargs.uid, cmdargs.tempDir,cmdargs.imageDir)
    
    analysisResults = doRegionAnalysis(results)
    
    #pdb.set_trace()
    fileName = "/scratch/rsc5/jason/regionalAnalysis/rainfall/all.csv"
    
    sendToOutput(results,fileName)
    
    sendToOutput(analysisResults,cmdargs.outputfile)

    #pdb.set_trace()


if __name__ == "__main__":
    main()

