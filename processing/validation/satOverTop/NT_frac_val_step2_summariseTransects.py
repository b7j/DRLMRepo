#!/usr/bin/env python

'''

This script gets teh output from step 1 and summarises it into a site by site form from the three transects i.e. averages the three transects fields

The output then needs to be intersected with a shapefile of lands 

./NT_frac_val_step2_summariseTransects.py --inputcsv outputTest.csv --outputcsv summarised.csv




'''

# get all the imports
import sys
import os
import argparse
import pdb
import xlrd
import re
import numpy as np
import csv
import collections

#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputcsv", help="Input csv file")

    
    p.add_argument("--outputcsv", help = "output tcsv file")

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
		       


def analysis(data):
           
    averaged = []
    
    siteIds = data['siteId']
    
    dates = data['date']
    
    #trans = data['trans']
    
    keys = data.keys()
    
    values = data.values()
    
    values = np.array(values)
    
    
    
    newDict = {}
    
    matched = []
	
    #pdb.set_trace()	
	
    #loop to get indexs of mathcing dates and siteIds for each site
	
    for d in range(len(dates)):	
	    
	    	print str(d)
	    
	    	dateIndex = []
	
		for ii in range(len(dates)):
				
			a = dates[d]
				
			if a == dates[ii]:
					
				dateIndex.append(ii)
				
				
				
		siteIndex = []
			
		for ii in range(len(siteIds)):
				
			a = siteIds[d]
				
			if a == siteIds[ii]:
					
				siteIndex.append(ii)
				
		#pdb.set_trace()		
				
		match = set(dateIndex).intersection(siteIndex)#from the indexs only get the index that have the same date and siteID	
		match = list(match)			
		#use the matched list to get the calculation values
		
		#pdb.set_trace()
		
		test = 0
		
		for m in match:
			
			for mm in matched:
				
				if m == mm:
					
					test += 1
					
		if test < 3:
			
			for m in match:
					
				matched.append(m)
				
			calcs = []
			
			#pdb.set_trace()
			
			for item in keys:
				
				aa = data[item]
				
				vals = []
				print item
				
				#item = 'transect'
				
				if item == 'transect':
					
					print 'skipping over transect text'
				
				elif item == 'lat':
					
					newDict.setdefault(item, [])
					
					b = aa[match[0]]
				
					newDict[item].append(b)
					
				elif item == 'long':
					
					newDict.setdefault(item, [])
					
					b = aa[match[0]]
				
					newDict[item].append(b)
					
				elif item == 'siteId':
					
					newDict.setdefault(item, [])
					
					b = aa[match[0]]
				
					newDict[item].append(b)
					
				elif item == 'date':
					
					newDict.setdefault(item, [])
					
					b = aa[match[0]]
				
					newDict[item].append(b)
					
				else:
					
					newDict.setdefault(item, [])
					
					vls = []
					
					for m in match:
						
						#pdb.set_trace()
						
						v = float(aa[m])
						
						vls.append(v)
									
					e = np.mean(vls)				
									
					newDict[item].append(e)
    return newDict		
	#pdb.set_trace()
    			
      
   
def getCsvData(fileName):
	    
	    
        with open(fileName, 'r') as f:
		
		reader = csv.reader(f)    
		
		mydict = collections.defaultdict(list)
		
		for row in reader:
			
			mydict[row[0]] = row[1:]
			
	return mydict		
			
	    
	    
	    


def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    # open the spreadsheet with transect data

    fileName = cmdargs.inputcsv
  
    myDict = getCsvData(fileName)
    
    #pdb.set_trace()

    result = analysis(myDict)

    #pdb.set_trace()
    
    

    fileName = cmdargs.outputcsv

    sendToOutput(result,fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()