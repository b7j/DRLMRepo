#!/usr/bin/env python


# get all the imports
import sys
import os
import argparse
import pdb
import xlrd
import re
import numpy as np

#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputxls", help="Input xls file")

    
    p.add_argument("--outputfile", help = "output text file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputxls is None:

        p.print_help()

        sys.exit()

    return cmdargs

    


def analysis(data):
    

    size = data.nrows
    
    sizeCols = data.ncols
    
    averaged = []
    
    
    
        

    for i in range(size):
	    
	siteIds = data.col_values(3,0,size)
		
	dates = data.col_values(2,0,size)
		
	trans = data.col_values(4,0,size)
		
	siteId = data.row_values(i,3,4)
	
	siteId = siteId[0]
	
	date = data.row_values(i,2,3)
	
	date = float(date[0])
	
	dateIndex = []
	
	#loop to get indexs of mathcing dates and siteIds for each site
	
	for ii in range(len(dates)):
		
		a = dates[ii]
		
		if a == date:
			
			dateIndex.append(ii)
	siteIndex = []
	
	for ii in range(len(siteIds)):
		
		a = siteIds[ii]
		
		if a == siteId:
			
			siteIndex.append(ii)
			
		
		
	
	match = set(dateIndex).intersection(siteIndex)#from the indexs only get the index that have the same date and siteID	
	
	#use the matched list to get the calculation values
	
	calcs = []
	
	for m in match:
		
		aa = data.row_values(m,5,sizeCols)
		
		calcs.append(aa)
	
	
	avg = np.mean(np.array(calcs), axis = 0)	
		
	
		
	match = list(match)
		
	header = data.row_values(match[0],0,4)
	
	avg = avg.tolist()
	
	for a in avg:
		
		header.append(a)
		
	#pdb.set_trace()	
	
	averaged.append(header)

    
    
           
    return averaged
                                
    

def sendToOutput(data,fileName):



    files = open(fileName, "w")
    
    for row in data:
	    
	#pdb.set_trace()
	
	rowStr = [str(x) for x in row]
	
	sites = ','.join(rowStr)
	
	files.write(sites + '\n')
    
    files.close()
  
   



def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    # open the spreadsheet with transect data

    xlFile = cmdargs.inputxls

    
    workbook = xlrd.open_workbook(xlFile)

    worksheets = workbook.sheet_names()

    data = workbook.sheet_by_name(worksheets[0])

     
    
    #pdb.set_trace()

    averaged = analysis(data)

    
       
    #pdb.set_trace()

    fileName = cmdargs.outputfile

    sendToOutput(averaged,fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()