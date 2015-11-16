#!/usr/bin/env python


# get all the imports
import sys
import os
import argparse
import datetime
import numpy as np
import pdb
import pandas
from collections import defaultdict
#import bokeh.plotting as bp
#from bokeh.models import HoverTool 
#from bokeh.charts import TimeSeries




#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputCsv", help="Input csv file from timetrace tool")
    
    p.add_argument("--identifier", help="uniqueIdentifier")
    
    p.add_argument("--outputDir", help="directory for output csvs")
    
    #p.add_argument("--outputcsv", help="Output csv file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputCsv is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
    
    
def doPlot(df,groupId,outputDir):
	     
     	     
	     
     for key, value in groupId.iteritems():
	     
	print key
	
	identifier = str(1)
	    
	stats = df['stats']
			
	newCol = df['stats'].apply(lambda x: pandas.Series(x.split(',')))
	
	bare = newCol[0]
	
	bare = list(bare[value])
	
	pv = newCol[2]
	
	pv = list(pv[value])
    
    	npv = newCol[1]
	
	npv = list(npv[value])
	
	date = df['season']
		
	date = date[value]
	
	fieldDate = df['date']
	
	fieldDate = list(fieldDate[value])
			
	siteId = df['siteId']
	
	siteId = list(siteId[value])
	
	#pdb.set_trace()
			
	fieldBare = df['fieldBare']*100
	
	fieldBare = list(fieldBare[value])
	
	fieldNPV = df['fieldNPV']*100
	
	fieldNPV = list(fieldNPV[value])
	
	fieldPV = df['fieldPV']*100
	
	fieldPV = list(fieldPV[value])
				
	newDates = []
	
	for i in date.values:
		
		i = str(i.tolist())
		
		year = i[0:4]
		
		month = i[4:6]
		
		day = str(1)
		
		newDates.append(day + '/' + month + '/' + year)
		
	rowList = siteId,newDates,fieldDate,bare,npv,pv,fieldBare,fieldNPV,fieldPV
	
	keys = 'siteId,imageDate,fieldDate,imageBareCover,imageNPVCover,imagePVCover,fieldBareCover,fieldNPVCover,fieldPVCover,'
    
	keyNames1 = keys.split(',')
	
	newDict = dict()
	
	
	for r in range(len(rowList)):
		
		row = rowList[r]
		
		for i in range(len(row)):
			
			k = keyNames1[r]
			
			rr = row[i]
			
			newDict.setdefault(k, [])
				
			newDict[k].append(rr)
		
	outputName = outputDir + key + '.csv'
	
	#pdb.set_trace()
	
	outdf = pandas.DataFrame(newDict)
    
    	outdf.to_csv(outputName)
	
	
	
	
	

		
		
	    
    
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    df = pandas.read_csv(cmdargs.inputCsv,header=0)
    
    #pdb.set_trace()
       
    grouping = df.groupby(cmdargs.identifier)
     
    groupId = grouping.groups
    
    doPlot(df,groupId,cmdargs.outputDir)
    
    
    pdb.set_trace()
        
        
if __name__ == "__main__":
    mainRoutine()

