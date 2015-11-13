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
import pandas
#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--csv", help="Input csv file")

    p.add_argument("--lookup", help="Input xls file")

    p.add_argument("--outputfile", help = "output csv file")

    cmdargs = p.parse_args()
    
    if cmdargs.csv is None:

        p.print_help()

        sys.exit()

    return cmdargs

def doTransect(data,interUnique):

    #pdb.set_trace()
    
    size = len(data)

    newArray = np.zeros((len(data),len(interUnique)))

    #pdb.set_trace()

    for i in range(len(data)): #each intercept

       b = data[i].split(',')
       

       for ii in b: # each component of the intercept

           for iii in range(len(interUnique)): # for each component loop through the lookup list and match


              if ii == interUnique[iii]:
                  
                  #pdb.set_trace()

                  newArray[i,iii] = 1

    return newArray                              

    
def fracAnalysis(result,lookup):

    #This is the basic fractional analysis calculation
    
    
    
    bareInd = [i for i, j in enumerate(lookup) if j == 'bare']
    
    pvInd = [i for i, j in enumerate(lookup) if j == 'pv']
    
    pvsInd = [i for i, j in enumerate(lookup) if j == 'pvs']#shrub
    
    pvInd.append(pvsInd[0])
    
    npvInd = [i for i, j in enumerate(lookup) if j == 'npv']
    
    npvsInd = [i for i, j in enumerate(lookup) if j == 'npvs']#shrub
    
    npvInd.append(npvsInd[0])
    
    crypInd = [i for i, j in enumerate(lookup) if j == 'crypt']

    summed = np.sum(result,0)

    summed.tolist()
    
    bare = []
    
    for i in bareInd:
	    
	    bare.append(summed[i])
	    
    pv = []
    
    for i in pvInd:
	    
	    pv.append(summed[i])
	    
    
	    
    npv = []
    
    for i in npvInd:
	    
	    npv.append(summed[i])
	    
    	    
    cryp = []
    
    for i in crypInd:
	    
	    cryp.append(summed[i])
	   
    #pdb.set_trace()
      
    return sum(bare),sum(cryp),sum(pv),sum(npv)
         
 
     
def woodyCoverAnalysis(result,lookup):


    #This step calcluates the woody components and adjusts the fractional cover based on an overtopping logic
    
    mgInd = [i for i, j in enumerate(lookup) if j == 'mg']
    
    mgdInd = [i for i, j in enumerate(lookup) if j == 'mgd']
    
    ogInd = [i for i, j in enumerate(lookup) if j == 'og']
    
    ogdInd = [i for i, j in enumerate(lookup) if j == 'ogd']
    
    canopyGreenInd = [mgInd,ogInd,mgdInd]
    
    mbInd = [i for i, j in enumerate(lookup) if j == 'mb']
    
    obInd = [i for i, j in enumerate(lookup) if j == 'ob']
        
    canopyBranchInd = [mbInd,obInd]
    
    mdInd = [i for i, j in enumerate(lookup) if j == 'md']
    
    odInd = [i for i, j in enumerate(lookup) if j == 'od']
        
    canopyDeadInd = [mdInd,odInd]
    
    mgSInd = [i for i, j in enumerate(lookup) if j == 'pvs']
    
    
        
    midGreenAllInd = [mgSInd,mgdInd,ogInd]
    
    oddInd = [i for i, j in enumerate(lookup) if j == 'odd']
    
    mddInd = [i for i, j in enumerate(lookup) if j == 'mdd']
        
    midDeadAllInd = [oddInd,mddInd]
    
    dsInd = [i for i, j in enumerate(lookup) if j == 'npvs']
    
    obdInd = [i for i, j in enumerate(lookup) if j == 'obd']
    
    mbdInd = [i for i, j in enumerate(lookup) if j == 'mbd']
    
        
    midBranchAllInd = [dsInd,obdInd,mbdInd]
    
     
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
	
        canopyGreen =  [] #woody green fraction
		
	for i in canopyGreenInd:
	    
	    canopyGreen.append(a[i])
	    
	nCanopyGreen = int(sum(canopyGreen))    
	
	#pdb.set_trace()
	
	if nCanopyGreen > 1:
		
		nCanopyGreen = 1
		
	nCanopyGreenAll.append(nCanopyGreen)
	
	canopyBranch =  [] #woody green fraction
		
	for i in canopyBranchInd:
	    
	    canopyBranch.append(a[i])
	    
	nCanopyBranch = int(sum(canopyBranch))    
	
	#pdb.set_trace()
	
	if nCanopyBranch > 1:
		
		nCanopyBranch = 1
		
	nCanopyBranchAll.append(nCanopyBranch)
		
	canopyDead =  [] #woody green fraction
		
	for i in canopyDeadInd:
	    
	    canopyDead.append(a[i])
	    
	nCanopyDead = int(sum(canopyDead))    
	
	#pdb.set_trace()
	
	if nCanopyDead > 1:
		
		nCanopyDead = 1
		
	nCanopyDeadAll.append(nCanopyDead)
	
	midGreen =  [] #woody green fraction
		
	for i in midGreenAllInd:
	    
	    midGreen.append(a[i])
	    
	nMidGreen = int(sum(midGreen))
	
    	nMidGreenAll.append(nMidGreen)
	
	midDead =  [] 
		
	for i in midDeadAllInd:
	    
	    midDead.append(a[i])
	    
	nMidDead = int(sum(midDead))
	
    	nMidDeadAll.append(nMidDead)
	
	midBranch =  [] 
		
	for i in midBranchAllInd:
	    
	    midBranch.append(a[i])
	    
	nMidBranch = int(sum(midBranch))
	
    	nMidBranchAll.append(nMidBranch)	
    	    
    #pdb.set_trace()
	    
    nCanopyGreenAll = sum(nCanopyGreenAll)
    
    nCanopyBranchAll = sum(nCanopyBranchAll)
    
    nCanopyDeadAll = sum(nCanopyDeadAll)
    
    nMidGreenAll = sum(nMidGreenAll)
    
    nMidDeadAll = sum(nMidDeadAll)
    
    nMidBranchAll = sum(nMidBranchAll)
    

    return nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll

    
    
# Analysis builds an array containing the idnividual intercepts

def analysis(dataMatrix,lookup1,lookup2,siteDetails):
    

    
    [rowNumber,colNumber] = np.shape(dataMatrix)
    
    rowList = []
    
    keyNames = 'lat,longt,date,siteId,bare,cryp,pV2,npV2,nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll'
    
    keyNames1 = keyNames.split(',')
       
    for i in range(rowNumber):

            #pdb.set_trace()
	    
	    #i = 18	    
		    
	    intercepts = dataMatrix[i,:]	     # get all the intercept row by row
	    
            result = doTransect(intercepts,lookup1)
            	    
	    lat = siteDetails['lat'][i]
	    
	    longt = siteDetails['longt'][i]
	    
	    date = siteDetails['date'][i]
	    
	    siteId = siteDetails['siteId'][i]
	      
	    bare,cryp,pV2,npV2 = fracAnalysis(result,lookup2)
	    
	    nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll = woodyCoverAnalysis(result,lookup2)
	    	     
	    row = [lat,longt,date,siteId,bare,cryp,pV2,npV2,nCanopyGreenAll,nCanopyBranchAll,nCanopyDeadAll,nMidDeadAll,nMidGreenAll,nMidBranchAll]
	    
	    
	    
	    rowList.append(row)
           
    return rowList, keyNames1
                                
    


def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function        
 
    data = pandas.read_csv(cmdargs.csv,header=0)
    
    keys = data.keys().tolist()
        
    interceptInd = [s for s in keys if "intercept" in s]
    
    intercepts = data[interceptInd]
    
    dataMatrix = pandas.DataFrame.as_matrix(intercepts)
    
    siteDetails = data[['lat','longt','siteId','date','property']]
               
    lookup = pandas.read_csv(cmdargs.lookup,header=0)
    
    lookup1 = []
    
    lookup2 = []
    
    for name, group in lookup.groupby(['NewVals','fraction']):
	    
	    lookup1.append(name[0])
	    
	    lookup2.append(name[1])
     
      
    rowList, keys = analysis(dataMatrix,lookup1,lookup2,siteDetails)
          
    newDict = dict()
     
    for row in rowList:
	    
	    #pdb.set_trace()
	    
	    for i in range(len(row)):
		    
		    k = keys[i]
		    
		    r = row[i]
		    
		    newDict.setdefault(k, [])
		    	    
	    	    newDict[k].append(r)
	               
    #pdb.set_trace()

    fileName = cmdargs.outputfile
        
    
    df = pandas.DataFrame(newDict)
    
    df.to_csv(fileName)

    #sendToOutput(newDict,fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()