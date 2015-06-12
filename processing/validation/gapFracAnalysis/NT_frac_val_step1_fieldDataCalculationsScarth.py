#!/usr/bin/env python

'''

./NT_frac_val_step1_fieldDataCalculations.py --inputxls /scratch/rsc5/jason/validation/Calculations/AllSitesStandardised2801pm.xls --inputlookup /scratch/rsc5/jason/validation/Calculations/uniqueList.xls --outputfile Step1FieldDataCalcs.csv 

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

#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputxls", help="Input xls file")

    p.add_argument("--inputlookup", help="Input xls file")

    p.add_argument("--outputfile", help = "output csv file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputxls is None:

        p.print_help()

        sys.exit()

    return cmdargs

def doTransect(data,interUnique):

    size = len(data)

    newArray = np.zeros((len(data),len(interUnique)))

    #pdb.set_trace()

    for i in range(len(data)): # each intercept

       b = data[i].split(',')
       

       for ii in b: # each component of the intercept

           for iii in range(len(interUnique)): # for each component loop through the lookup list and match


              if ii == interUnique[iii]:
                  
                  #pdb.set_trace()

                  newArray[i,iii] = 1

    return newArray                              

    
def fracAnalysis(result):

    #This is the basic fractional analysis calculation

    summed = np.sum(result,0)

    summed.tolist()

    bare = summed[0] + summed[8] + summed[19] + summed[25] + summed[27] + summed[28]

    
    pV2 = summed[9] + summed[10] + summed[11] + summed[13] + summed[14] + summed[26]

    
    npV2 = summed[1] + summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[23] + summed[30]
        
    cryp = summed[24]

    
  
    return bare,cryp,pV2,npV2
         
 
     
def woodyCoverAnalysis(result):


    #This step calcluates the woody components and adjusts the fractional cover based on an overtopping logic
    
    size = result.shape

    row = size[0]

    fpcStage1 = []

    ppcStage1 = []

    ccStage1 = []
    
    pv1_2 = []
    
    pvT = []
    
    npvT = []
    
    npv2 = [] 
    
    npvWoody_mid_over =[]
    
    bareT = []
    
    nCanopyGreenAll = []
    
    nCanopyBranchAll = []
    
    nCanopyDeadAll = []
    
    nMidGreenAll = []

    nMidBranchAll = []
    
    nMidDeadAll = []

    #loop through the matrix add up each woody component

    for i in range(row):
	    
	a = result[i,:]

        nCanopyGreen =  a[18] + a[22] + a[39] #woody green fraction
	
	if nCanopyGreen > 1:
		
		nCanopyGreen = 1
		
	nCanopyGreenAll.append(nCanopyGreen)
		
	nCanopyBranch =  a[16] + a[20] 
		
	if nCanopyBranch > 1:
		
		nCanopyBranch = 1 
		
	nCanopyBranchAll.append(nCanopyBranch)
	
	nCanopyDead =  a[17] + a[21] 
		
	if nCanopyDead > 1:
		
		nCanopyDead = 1 
		
	nCanopyDeadAll.append(nCanopyDead)
	
    	nMidGreenAll.append(a[12] + a[36] + a[39])
	
    	nMidDeadAll.append(a[35] + a[38])
	
    	nMidBranchAll.append(a[7] + a[34] + a[37])
    
    nCanopyGreenAll = sum(nCanopyGreenAll)
    
    nCanopyBranchAll = sum(nCanopyBranchAll)
    
    nCanopyDeadAll = sum(nCanopyDeadAll)
    
    nMidGreenAll = sum(nMidGreenAll)
    
    nMidDeadAll = sum(nMidDeadAll)
    
    nMidBranchAll = sum(nMidBranchAll)
    

    return nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll

    
    
# Analysis builds an array containing the idnividual intercepts

def analysis(data,interUnique):
    

    size = data.nrows
    
    rowList = []
    
    keyNames = 'lat,longt,date,siteId,trans,bare,cryp,pV2,npV2,nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll'
    
    keyNames1 = keyNames.split(',')
    
    dictionary = dict.fromkeys(keyNames1, 0)
    
        

    for i in range(size):

            #i = 2499
	    
	    intercepts = data.row_values(i,5,105) # get all the intercept row by row

            result = doTransect(intercepts,interUnique)

            siteDetails = data.row_values(i,0,5) # get all the site details
	    
	    #pdb.set_trace()
	    
	    lat = data.row_values(i,0,1)
	    
	    lat = lat[0]
	    
	    longt = data.row_values(i,1,2)
	    
	    longt = longt[0]
	    
	    date = data.row_values(i,2,3)
	    
	    date = date[0]
	    
	    siteId = data.row_values(i,3,4)
	    
	    siteId = siteId[0]
	    
	    trans = data.row_values(i,4,5)
	    
	    trans = trans[0]
	   	    
	   
	        
	    #pdb.set_trace()
	    
	    bare,cryp,pV2,npV2 = fracAnalysis(result)
	    
	    nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll = woodyCoverAnalysis(result)
	    	     
	    row = [lat,longt,date,siteId,trans,bare,cryp,pV2,npV2,nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll]
	    
	    
	    
	    rowList.append(row)
	    
	    

    
    
           
    return rowList, keyNames1
                                
    



def getLookUp(data):

    #pdb.set_trace()

    oldVals =  data.col_values(0,0,None)

    

    return oldVals



def sendToOutput(myDict,fileName):

        with open(fileName, 'w') as f:
	
		writer = csv.writer(f)  
		  
		for k,v in myDict.iteritems():
			
			writer.writerow([k] + v)               
		       
		       
		       
		       
		       
		       
		       
		       
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function        

    # open the spreadsheet with transect data

    xlFile = cmdargs.inputxls

    
    workbook = xlrd.open_workbook(xlFile)

    worksheets = workbook.sheet_names()

    data = workbook.sheet_by_name(worksheets[0])

    
   #Open the unique list

    xlFile = cmdargs.inputlookup
    
    workbook = xlrd.open_workbook(xlFile)

    worksheets = workbook.sheet_names()

    data2 = workbook.sheet_by_name(worksheets[0])

    


    interUnique = getLookUp(data2)
    
    #pdb.set_trace()

    rowList, keys = analysis(data,interUnique)
        
    newDict = dict()
    
    #newDict.fromkeys(keys, 0)
    
    #pdb.set_trace()
    
    for row in rowList:
	    
	    #pdb.set_trace()
	    
	    for i in range(len(row)):
		    
		    k = keys[i]
		    
		    r = row[i]
		    
		    newDict.setdefault(k, [])
		    	    
	    	    newDict[k].append(r)
	               
    #pdb.set_trace()

    fileName = cmdargs.outputfile

    sendToOutput(newDict,fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()