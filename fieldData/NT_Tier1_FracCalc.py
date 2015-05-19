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

    p.add_argument("--inputlookup", help="Input xls file")

    p.add_argument("--outputfile", help = "output text file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputxls is None:

        p.print_help()

        sys.exit()

    return cmdargs

def doTransect(data,interUnique):

    size = len(data)

    newArray = np.zeros((len(data),len(interUnique)))

    

    for i in range(len(data)): # each intercept

       #pdb.set_trace()

       

       b = data[i].split(',')
       

       for ii in b: # each component of the intercept

           for iii in range(len(interUnique)): # for each component loop through the lookup list and match


              if ii == interUnique[iii]:
                  
                  #pdb.set_trace()

                  newArray[i,iii] = 1

                  

                 
    return newArray                              
    
def fracAnalysis(result):

    #pdb.set_trace()

    summed = np.sum(result,0)

    summed.tolist()

    bare = summed[0] + summed[8] + summed[19] + summed[24] + summed[25] + summed[27] + summed[28]

    lit = summed[23] # litter

    pG = summed[6] + summed[11] # pv and npv perennial grass 

    aG = summed[2] + summed[10] # pv and npv annual grass

    aF = summed[3] + summed[13] # pv and npv annual forb/herb

    pF = summed[14] + summed[30] # pv and npv prennial forb/herb

    gvc = summed[1] + summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[9] + summed[10] + summed [11] + summed [12] + summed[13] + summed[14] + summed[26] + summed[30] # total ground vegetation cover

    tmc = summed[16] + summed[17] + summed[18] + summed[37] + summed[38] + summed[39] + summed[40] + summed[41] # total mid cover

    tuc = summed[15] + summed[20] + summed[21] + summed[22] # total crown cover for upper stratum
    
    ls = summed[1] + summed[7] + summed[12] # low shrub calculation as per ipad calulation 2014 version

    pV1 = summed[9] + summed[10] + summed[11] + summed[12] + summed[13] + summed[14] + summed[26]

    npV1 = summed[1] + summed[2] + summed[2] + summed[4] + summed[5] + summed[6] + summed[7] + summed[23] + summed[30]

    bal =  summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[30] + summed[34] + summed[35] # Brown Attached Leaf

    bdl = summed[1] + summed[23] # brown detached leaf

    bareSoil = summed[0] + summed[8] + summed[25]

    agg = summed[27] + summed[28]

    cryp = summed[24]

    ash = summed[19]

    branch = summed[16] + summed[20]

    ppcWork = summed[7] + summed[16] + summed[17] + summed[20] + summed[21] + summed[34] + summed[35] + summed[37] + summed[38] #workings for ppc

    ccWork = summed[15]

    

    return bare, lit, pG, aG, aF, pF, gvc, tmc, tuc, ls, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch, ppcWork, ccWork
     
def woodyCoverAnalysis(result,branch,ppcWork,ccWork):

    
    size = result.shape

    row = size[0]

    aa = []

    

    for i in range(row):

        a = result[i,:]

        b = a[12] + a[18] + a[22] + a[36] + a[39]

        aa.append(b)

    

    newList = []

    for i in aa:

        if i == 0:

           newList.append(1)

    #pdb.set_trace()

    summed = sum(newList)

    fpc1 = 100 - summed

    fpcQ = fpc1 / (100 - branch)

    fpcQ = fpcQ * 100

    ppc = fpc1 + ppcWork

    cc = ppc + ccWork


    return fpc1, fpcQ, ppc, cc

    

   
    
    


def analysis(data,interUnique):
    

    size = data.nrows
    
    rowList = []
    
    
    
        

    for i in range(size):

        

            intercepts = data.row_values(i,5,105) # get all the intercept row by row

            result = doTransect(intercepts,interUnique)

            siteDetails = data.row_values(i,0,5) # get all the site details
	    
            rowStr = [str(x) for x in siteDetails]
	    
            sites = ','.join(rowStr)
	    
            bare, lit, pG, aG, aF, pF, gvc, tmc, tuc, ls, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch, ppcWork, ccWork = fracAnalysis(result)
         
            fpc1, fpcQ, ppc, cc = woodyCoverAnalysis(result, branch, ppcWork, ccWork)
	    
            row = [sites,bare, lit, pG, aG, aF, pF, gvc, tmc, tuc, ls, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch, fpc1, fpcQ, ppc, cc]
	    
            rowList.append(row)
	    
	    

    
    
           
    return rowList
                                
    



def getLookUp(data):

    #pdb.set_trace()

    oldVals =  data.col_values(0,0,None)

    

    return oldVals



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

    xlFile = cmdargs.inputxls

    
    workbook = xlrd.open_workbook(xlFile)

    worksheets = workbook.sheet_names()

    data = workbook.sheet_by_name(worksheets[0])

    


    xlFile = cmdargs.inputlookup
    
    workbook = xlrd.open_workbook(xlFile)

    worksheets = workbook.sheet_names()

    data2 = workbook.sheet_by_name(worksheets[0])

    


    interUnique = getLookUp(data2)
    
    #pdb.set_trace()

    rowList = analysis(data,interUnique)

    
       
    #pdb.set_trace()

    fileName = cmdargs.outputfile

    sendToOutput(rowList,fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()