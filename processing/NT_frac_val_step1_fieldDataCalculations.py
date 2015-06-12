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
    
def gapFracAnalysis(result):
	
	#as per Peter Scarth's Gap Fraction Analysis
	
	summed = np.sum(result,0)
	
	summed.tolist()
	
	nTotal = 100 #this is set 100 as all our sites have been cleaned to ensure 100 intercepts per transect
	
	#down
		
	bare = summed[0] + summed[8] + summed[19] + summed[25] + summed[27] + summed[28] # note removed crypto & added to npV1
	
	pV1 = summed[9] + summed[10] + summed[11] + summed[12] + summed[13] + summed[14] + summed[26]
	
	npV1 = summed[1] + summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[23] + summed[30] + summed[24]
	
	#pdb.set_trace()
	
	#over
	
	nCanopyGreen = (summed[22] + summed[36])*nTotal/100
	
	nCanopyDead = (summed[21]+ summed[35])*nTotal/100
	
	nCanopyBranch = (summed[20] + summed[34])*nTotal/100
	
	nMidGreen = (summed[18] + summed[39])*nTotal/100
	
	nMidDead = (summed[17] + summed[38])*nTotal/100
	
	nMidBranch = summed[16]*nTotal/100
		
	
	
	nGroundCrustDistRock = bare*nTotal/100
	
	nGroundGreen = pV1*nTotal/100
	
	nGroundDeadLitter= npV1*nTotal/100
	
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
	
	groundPVCover=nGroundGreen/nTotal
	groundNPVCover=nGroundDeadLitter/nTotal
	groundBareCover=nGroundCrustDistRock/nTotal
	groundTotalCover=(nGroundGreen+nGroundDeadLitter+nGroundCrustDistRock)/nTotal
	
	#pdb.set_trace()
	
	satGroundPVCover=groundPVCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	satGroundNPVCover=groundNPVCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	satGroundBareCover=groundBareCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	satGroundTotalCover=groundTotalCover*(1-midPlantProjectiveCover)*(1-canopyPlantProjectiveCover)
	
	satGroundPVCover= satGroundPVCover + canopyPlantProjectiveCover + midPlantProjectiveCover
	satGroundTotalCover= satGroundPVCover + satGroundNPVCover + satGroundBareCover
		
	totalPVCover=canopyFoliageProjectiveCover+satMidFoliageProjectiveCover+satGroundPVCover
	totalNPVCover=canopyDeadProjectiveCover+canopyBranchProjectiveCover+satMidDeadProjectiveCover+satMidBranchProjectiveCover+satGroundNPVCover
	totalBareCover=satGroundBareCover
	
	# Round things back to 0 to 100
	satGroundPVCover = satGroundPVCover*100
	satGroundNPVCover = satGroundNPVCover*100
	satGroundBareCover = satGroundBareCover*100
	satGroundTotalCover = satGroundTotalCover*100
	
	totalPVCover = totalPVCover*100
	totalNPVCover = totalNPVCover*100
	totalBareCover = totalBareCover*100

	return totalPVCover,totalNPVCover,totalBareCover,satGroundPVCover,satGroundNPVCover,satGroundBareCover,satGroundTotalCover
    
    
def fracAnalysis(result):

    #This is the basic fractional analysis calculation

    summed = np.sum(result,0)

    summed.tolist()

    bare = summed[0] + summed[8] + summed[19] + summed[25] + summed[27] + summed[28]

    pV1 = summed[9] + summed[10] + summed[11] + summed[12] + summed[13] + summed[14] + summed[26]

    npV1 = summed[1] + summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[23] + summed[24] + summed[30]

    bal =  summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[30] + summed[34] + summed[35] # Brown Attached Leaf

    bdl = summed[1] + summed[23] # brown detached leaf

    bareSoil = summed[0] + summed[8] + summed[25]

    agg = summed[27] + summed[28]

    cryp = summed[24]

    ash = summed[19]

    branch = summed[16] + summed[20]

  
    return bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch
     
def woodyCoverAnalysis(result,branch):


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
    
    

    #loop through the matrix add up each woody component

    for i in range(row):
	    
	a = result[i,:]

        b = a[12] + a[18] + a[22] + a[36] + a[39] #woody green fraction
	
	if b > 1:
		
		b = 1

        c = a[12] + a[18] + a[22] + a[36] + a[39] + a[7] + a[16] + a[17] + a[20] + a[21] + a[34] + a[35] + a[37] + a[38] #plant projective cover - woody and green
	
	if c >1:
		
		c = 1

        d = a[12] + a[18] + a[22] + a[36] + a[39] + a[7] + a[16] + a[17] + a[20] + a[21] + a[34] + a[35] + a[37] + a[38] + a[15]
	 #canopy cover - PPC, incrown, mid-incrown
	 
	bare = a[0] + a[8] + a[19] + a[24] + a[25] + a[27] + a[28] 
	
	
	 
	npV1 = a[1] + a[2] + a[3] + a[4] + a[5] + a[6] + a[7] + a[23] + a[30]
 	
	pV1 = a[9] + a[10] + a[11] + a[12] + a[13] + a[14] + a[26]
	
	pvtemp = pV1 - c
	
	if pvtemp < 0:
		
		pvtemp = 0
	
	pvtemp2 = pvtemp + b	
	
	npvWoody_mid_overTemp = c - b
	
	npv2Temp = npV1 - c
	
	if npv2Temp <0:
	
		npv2Temp = 0
		
	npvTTemp = npv2Temp + npvWoody_mid_overTemp
	
	bareTTemp = bare - (pvtemp2 + npvTTemp)
	
	if bareTTemp <0:
		
		bareTTemp = 0
		
	#pdb.set_trace()
	
	bareT.append(bareTTemp)
	
	npvT.append(npvTTemp)
    
    	npv2.append(npv2Temp)
    
    	npvWoody_mid_over.append(npvWoody_mid_overTemp)
	
	pv1_2.append(pvtemp)
	
	pvT.append(pvtemp2)

        fpcStage1.append(b)

        ppcStage1.append(c)

        ccStage1.append(d)
	
	

    #Next is to replace all the zero intercepts for each woody component and replace with a 1 for the purpose of removing from the total sum

    #pdb.set_trace()
    
    
    fpcStage2 = []

    for i in fpcStage1:

        if i == 0:

           fpcStage2.append(1)

    
    ppcStage2 = []

    for i in ppcStage1:

        if i == 0:

           ppcStage2.append(1)

    
    ccStage2 = []

    for i in ccStage1:

        if i == 0:

           ccStage2.append(1)


   #sum all the zero hits together

    #pdb.set_trace()
    sumFpc = sum(fpcStage2)

    sumPpc = sum(ppcStage2)

    sumCc = sum(ccStage2)
    
    sumPv1_2 = sum(pv1_2)
    
    sumPvT = sum(pvT)
    
    sumbareT = sum(bareT)
    
    sumnpvT = sum(npvT)
    
    sumnpv2 = sum(npv2)
    
    sumnpvWMO = sum(npvWoody_mid_over)
    
    
    

    #final calculation of each woody component allowing for over topping.

    fpc1 = 100 - sumFpc # 

    fpcQ = fpc1 / (100 - branch)

    fpcQ = fpcQ * 100

    ppc = 100 - sumPpc

    cc = 100 - sumCc
    
    

    return fpc1,fpcQ,ppc,cc,sumbareT,sumnpvT,sumnpv2,sumnpvWMO,sumPv1_2,sumPvT

    
    
# Analysis builds an array containing the idnividual intercepts

def analysis(data,interUnique):
    

    size = data.nrows
    
    rowList = []
    
    keyNames = 'lat,long,date,siteId,transect,bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch, fpc1, fpcQ, ppc, cc,satBARE_NT,satNPV_NT,sumnpv2,sumnpvWMO,sumPv1_2,satPV_NT,totalPVCoverQLD,totalNPVCoverQLD,totalBareCoverQLD,satGroundPVCoverQLD,satGroundNPVCoverQLD,satGroundBareCoverQLD,satGroundTotalCoverQLD'
    
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
	    
	    bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch = fracAnalysis(result)
	    
	    fpc1, fpcQ, ppc, cc,sumbareT,sumnpvT,sumnpv2,sumnpvWMO,sumPv1_2,sumPvT = woodyCoverAnalysis(result, branch)
	    
	    totalPVCover,totalNPVCover,totalBareCover,satGroundPVCover,satGroundNPVCover,satGroundBareCover,satGroundTotalCover = gapFracAnalysis(result)
	    
	    row = [lat,longt,date,siteId,trans,bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch, fpc1, fpcQ, ppc, cc,sumbareT,sumnpvT,sumnpv2,sumnpvWMO,sumPv1_2,sumPvT,totalPVCover,totalNPVCover,totalBareCover,satGroundPVCover,satGroundNPVCover,satGroundBareCover,satGroundTotalCover]
	    
	    
	    
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