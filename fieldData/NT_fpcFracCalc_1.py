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

    pV1 = summed[9] + summed[10] + summed[11] + summed[12] + summed[13] + summed[14] + summed[26]

    npV1 = summed[1] + summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[23] + summed[30]

    bal =  summed[2] + summed[3] + summed[4] + summed[5] + summed[6] + summed[7] + summed[30] + summed[34] + summed[35] # Brown Attached Leaf

    bdl = summed[1] + summed[23] # brown detached leaf

    bareSoil = summed[0] + summed[8] + summed[25]

    agg = summed[27] + summed[28]

    cryp = summed[24]

    ash = summed[19]

    branch = summed[16] + summed[20]

  
    return bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch
     
def woodyCoverAnalysis(result,branch):


    #pdb.set_trace()
    
    size = result.shape

    row = size[0]

    fpcStage1 = []

    ppcStage1 = []

    ccStage1 = []

    #loop through the matrix add up each woody component

    for i in range(row):

        a = result[i,:]

        b = a[12] + a[18] + a[22] + a[36] + a[39]

        c = a[12] + a[18] + a[22] + a[36] + a[39] + a[7] + a[16] + a[17] + a[20] + a[21] + a[34] + a[35] + a[37] + a[38]

        d = a[12] + a[18] + a[22] + a[36] + a[39] + a[7] + a[16] + a[17] + a[20] + a[21] + a[34] + a[35] + a[37] + a[38] + a[15]

        fpcStage1.append(b)

        ppcStage1.append(c)

        ccStage1.append(d)

    #Next is to replace all the zero intercepts for each woody component and replace with a 1 for the purpose of removing from the total sum

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

    sumFpc = sum(fpcStage2)

    sumPpc = sum(ppcStage2)

    sumCc = sum(ccStage2)

    #final calculation of each woody component allowing for over topping.

    fpc1 = 100 - sumFpc # 

    fpcQ = fpc1 / (100 - branch)

    fpcQ = fpcQ * 100

    ppc = 100 - sumPpc

    cc = 100 - sumCc


    return fpc1, fpcQ, ppc, cc

    

   
    
    


def analysis(data,interUnique):
    

    size = data.nrows
    
    rowList = []
    
    
    
        

    for i in range(size):

            #pdb.set_trace()

            intercepts = data.row_values(i,5,105) # get all the intercept row by row

            result = doTransect(intercepts,interUnique)

            siteDetails = data.row_values(i,0,5) # get all the site details
	    
	    rowStr = [str(x) for x in siteDetails]
	    
	    sites = ','.join(rowStr)
	    
	    bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch = fracAnalysis(result)
	    
	    fpc1, fpcQ, ppc, cc = woodyCoverAnalysis(result, branch)
	    
	    row = [sites,bare, pV1, npV1, bal, bdl, bareSoil, agg, cryp, ash, branch, fpc1, fpcQ, ppc, cc]
	    
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

    rowList = analysis(data,interUnique)

    
       
    #pdb.set_trace()

    fileName = cmdargs.outputfile

    sendToOutput(rowList,fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()