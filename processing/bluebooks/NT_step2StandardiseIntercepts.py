#!/usr/bin/env python
'''
This script standarises intercept names using the input lookup spreadsheet called lookupTable.csv
'''


# get all the imports
import sys
import os
import argparse
import pdb
import xlrd
import re
import pandas
import numpy as np

#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--csv", help="Input csv file")

    p.add_argument("--lookup", help="Input lookup file")

    p.add_argument("--outputfile", help = "output text file")

    cmdargs = p.parse_args()
    
    if cmdargs.csv is None:

        p.print_help()

        sys.exit()

    return cmdargs

def replace_all(text, dic):

    interA = text.split(',')

    interB = []

    #pdb.set_trace()

    for ii in interA:

        for i, j in dic.iteritems():

              i = str(i)              

              j = str(j)

              match = ii == i

              if  match  == True:

                  interB.append(j)

      
            


    newList = ",".join(interB)
    
    return newList 



def analysis(dataMatrix,oldVals,newVals,siteDetails):
    
    transectOutputs = []

    [rowNumber,colNumber] = np.shape(dataMatrix)
            
    dictionary = dict(zip(oldVals, newVals))

    allSites = []

    for i in range(rowNumber):

	intercepts = dataMatrix[i,:]	     # get all the intercept row by row
	    	
	lat = str(siteDetails['lat'][i])
	    
	longt = str(siteDetails['longt'][i])
	    
	date = siteDetails['date'][i]
	    
	siteId = siteDetails['siteId'][i]
	
	property = siteDetails['property'][i]
		
	print siteId
	
	outputs = [lat,longt,siteId,date,property]
           
                             
        for ii in range(len(intercepts)):

            aa = str(intercepts[ii])

            result = replace_all(aa,dictionary)

            result = str(result)
            
            outputs.append(result)
	    
	allSites.append(outputs)    
			
     
    return allSites


def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function
    
    data = pandas.read_csv(cmdargs.csv,header=0)
    
    keys = data.keys().tolist()
        
    interceptInd = [s for s in keys if "intercept" in s]
    
    intercepts = data[interceptInd]
    
    dataMatrix = pandas.DataFrame.as_matrix(intercepts)
    
    siteDetails = data[['lat','longt','siteId','date','property']]    
        
    lookup = pandas.read_csv(cmdargs.lookup,header=0)
    
    newVals = lookup['NewVals'].tolist()
    
    oldVals = lookup['oldVals'].tolist()
   
    rowList = analysis(dataMatrix,oldVals,newVals,siteDetails)

    newDict = dict()
    
    siteKeys = ['lat','longt','siteId','date','property']
    
    for i in interceptInd:
	    
	    siteKeys.append(i)
	    
    #pdb.set_trace()
     
    for row in rowList:
	    
	    #pdb.set_trace()
	    
	    for i in range(len(row)):
		    
		    k = siteKeys[i]
		    
		    r = row[i]
		    
		    newDict.setdefault(k, [])
		    	    
	    	    newDict[k].append(r)
	               
    #pdb.set_trace()

    fileName = cmdargs.outputfile
        
    
    df = pandas.DataFrame(newDict)
    
    df.to_csv(fileName)
    

    



        
if __name__ == "__main__":
    mainRoutine()