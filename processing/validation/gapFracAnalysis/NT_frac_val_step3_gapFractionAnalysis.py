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
		       
		       
		       
		       
		       
		       
		       
		       

  
   
def getCsvData(fileName):
	    
	    
        with open(fileName, 'r') as f:
		
		reader = csv.reader(f)    
		
		mydict = collections.defaultdict(list)
		
		for row in reader:
			
			mydict[row[0]] = row[1:]
			
	return mydict		
			
  
def gapFracAnalysis(result):
	
	#as per Peter Scarth's Gap Fraction Analysis
	#pdb.set_trace()
	
	nTotal = 300
	
	gnTotal = (np.array(result['nTotal']).astype(np.float))
			
	nCanopyGreen = (np.array(result['nCanopyGreenAll']).astype(np.float))*nTotal/100		
		
	nCanopyDead=(np.array(result['nCanopyDeadAll']).astype(np.float))*nTotal/100
	
	nCanopyBranch=(np.array(result['nCanopyBranchAll']).astype(np.float))*nTotal/100
	
	nMidGreen=(np.array(result['nMidGreenAll']).astype(np.float))*nTotal/100
	
	nMidDead=(np.array(result['nMidDeadAll']).astype(np.float))*nTotal/100
	
	nMidBranch=(np.array(result['nMidBranchAll']).astype(np.float))*nTotal/100
	
	nGroundCrustDistRock=(np.array(result['newBare']).astype(np.float))*gnTotal/100
	
	nGroundGreen=(np.array(result['newPV']).astype(np.float))*gnTotal/100
	
	nGroundDeadLitter=(np.array(result['newNPV']).astype(np.float))*gnTotal/100
	
	nGroundCrypto=(np.array(result['newCryp']).astype(np.float))*gnTotal/100
	
	# OK- I think we can add Crypto into the Dead and let the optimization work it out later
	nGroundDeadLitter=nGroundDeadLitter+nGroundCrypto
	
	canopyFoliageProjectiveCover=nCanopyGreen/(nTotal-nCanopyBranch)
	canopyDeadProjectiveCover=nCanopyDead/(nTotal-nCanopyBranch)
	canopyBranchProjectiveCover=nCanopyBranch/nTotal*(1-canopyFoliageProjectiveCover-canopyDeadProjectiveCover)
	canopyPlantProjectiveCover=(nCanopyGreen+nCanopyDead+nCanopyBranch)/nTotal
	
	midFoliageProjectiveCover=nMidGreen/nTotal
	midDeadProjectiveCover=nMidDead/nTotal
	midBranchProjectiveCover=nMidBranch/nTotal
	midPlantProjectiveCover=(nMidGreen+nMidDead+nMidBranch)/nTotal
	
	satMidFoliageProjectiveCover=midFoliageProjectiveCover*(1-canopyPlantProjectiveCover)
	satMidDeadProjectiveCover=midDeadProjectiveCover*(1-canopyPlantProjectiveCover)
	satMidBranchProjectiveCover=midBranchProjectiveCover*(1-canopyPlantProjectiveCover)
	satMidPlantProjectiveCover=midPlantProjectiveCover*(1-canopyPlantProjectiveCover)
	
	groundPVCover=nGroundGreen/gnTotal
	groundNPVCover=nGroundDeadLitter/gnTotal
	groundBareCover=nGroundCrustDistRock/gnTotal
	groundTotalCover=(nGroundGreen+nGroundDeadLitter+nGroundCrustDistRock)/gnTotal
	
	#pdb.set_trace()
	
	satGroundPVCover=groundPVCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	satGroundNPVCover=groundNPVCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	satGroundBareCover=groundBareCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	satGroundTotalCover=groundTotalCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	
	#satGroundPVCover= satGroundPVCover + canopyPlantProjectiveCover + midPlantProjectiveCover
	#satGroundTotalCover= satGroundPVCover + satGroundNPVCover + satGroundBareCover
		
	totalPVCover=canopyFoliageProjectiveCover+satMidFoliageProjectiveCover+satGroundPVCover
	totalNPVCover=canopyDeadProjectiveCover+canopyBranchProjectiveCover+satMidDeadProjectiveCover+satMidBranchProjectiveCover+satGroundNPVCover
	totalBareCover=satGroundBareCover
	totalCover = totalPVCover + totalNPVCover + totalBareCover
		
	#pdb.set_trace()

	return totalPVCover,totalNPVCover,totalBareCover,totalCover
    
    
# 
    	    
	    		       
		       
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function        

    # open the spreadsheet with transect data
    fileName = cmdargs.inputcsv
  
    myDict = getCsvData(fileName)
    
    totalPVCover,totalNPVCover,totalBareCover,totalCover = gapFracAnalysis(myDict)
    
    rowList = totalPVCover,totalNPVCover,totalBareCover,totalCover,myDict['lat'],myDict['longt'],myDict['date'],myDict['siteId']
    
    
    keys = 'totalPVCover,totalNPVCover,totalBareCover,totalCover,lat,longt,date,siteId'
    
    keyNames1 = keys.split(',')
    
    newDict = dict()
        
    #newDict.fromkeys(keys, 0)
    
    #pdb.set_trace()
    
    for r in range(len(rowList)):
	    
	    row = rowList[r]
	    
	    for i in range(len(row)):
		    
		    k = keyNames1[r]
		    
		    rr = row[i]
		    
		    newDict.setdefault(k, [])
		    	    
	    	    newDict[k].append(rr)
	               
    #pdb.set_trace()

    fileName = cmdargs.outputcsv

    sendToOutput(newDict,fileName)

    
    



        
if __name__ == "__main__":
    mainRoutine()