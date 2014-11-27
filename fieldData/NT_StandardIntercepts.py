#!/usr/bin/env python
'''
This script standarises intercept names using the input lookup spreadsheet called uniqueList.xls

'''


# get all the imports
import sys
import os
import argparse
import pdb
import xlrd
import re

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



def analysis(data,oldVals,newVals):
    

    size = data.nrows

    transectOutputs = []

    #pdb.set_trace()

    dictionary = dict(zip(oldVals, newVals))

    allSites = []

    for i in range(size):

        

        if i > 0:   # ignore header row       

            intercepts = data.row_values(i,7,107) # get all the intercept row by row

            siteDetails = data.row_values(i,0,7) # get all the site details

            allSites.append(siteDetails)

            
            interceptOutput = []
            
            #pdb.set_trace()
            #loop through each intercept
            
            for ii in range(len(intercepts)):

                aa = str(intercepts[ii])

                result = replace_all(aa,dictionary)

                result = str(result)

                #pdb.set_trace()

                #result = '"' + result
              
                interceptOutput.append(result)
                
                
            #pdb.set_trace()

            newList = ";".join(interceptOutput)
                
            transectOutputs.append(newList)
                    
    
    return transectOutputs, allSites


def getLookUp(data):

    #pdb.set_trace()

    oldVals =  data.col_values(0,0,None)

    newVals = data.col_values(1,0,None)

    return oldVals,newVals



def sendToOutput(data,fileName):

    files = open(fileName, "w")

    #pdb.set_trace()

    for i in data:

        ii = str(i)      
        
        files.write(ii + '\n')

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

    

    oldVals,newVals = getLookUp(data2)

    transectOutput, siteDetails = analysis(data,oldVals,newVals)

    
       
    #pdb.set_trace()

    fileName = cmdargs.outputfile

    sendToOutput(transectOutput,'transects2411.txt')

    sendToOutput(siteDetails,'siteDetails2411.txt')

    



        
if __name__ == "__main__":
    mainRoutine()