#!/usr/bin/env python
import pdb

import os

import argparse

import csv

from osgeo import ogr

import numpy as np

import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec

import matplotlib.colors as colors

from pylab import *

from time import gmtime, strftime




#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputImage", help="Input image")

    p.add_argument("--inputVector", help="Input shapefile of area to be analysed")

    p.add_argument("--uid", help="Shapefile unique ID")

    p.add_argument("--outputfile", help = "output text file")

    p.add_argument("--fieldName", help = "field name in shapefile with feature names for plotting")

    cmdargs = p.parse_args()
    
    if cmdargs.inputImage is None:

        p.print_help()

        sys.exit()

    return cmdargs
 

 
# Set up the function to be applied
def doCounts(filename,vec,uid):
   
   

    allCounts = []


    for i in range(10): 

        i = i+1

        print i

        print strftime("%H:%M:%S", gmtime())

        sample = str(i) + ',' + str(i)

        csvfile = "temp.csv"

        cmd = "qv_rastbypoly.py -r %s -v %s -c %s -o %s --samplerange %s --stats count,nullcount" % (filename, vec, uid, csvfile,sample)

        os.system(cmd)
        
        #pdb.set_trace()

        infile = open(csvfile, "rb") 

        reader = csv.reader(infile) 

        counts = []
  
        for row in reader:

            counts.append(row)
            
        allCounts.append(counts)
  
 
    
    #pdb.set_trace()

    return allCounts

def doTotals(ranks):

    allRanks = []

    for rank in ranks:

        #pdb.set_trace()

        districts = []

        distCounts = []

        distNulls = []

        for i in range(len(rank)):

           a = rank[i]

           districts.append(a[0])

           distCounts.append(a[1])

           distNulls.append(a[2])

        row = [districts,distCounts,distNulls]

        allRanks.append(row)


    return allRanks


def sendToOutput(data,fileName):

   
    files = open(fileName, "w")
    
    for row in data:
            
        #pdb.set_trace()
        
        rowStr = [str(x) for x in row]
        
        sites = ','.join(rowStr)
        
        files.write(sites + '\n')
    
    files.close()

def doCalcs(totals):

    counts = []

    nulls = []

    #pdb.set_trace()

    rowSize = len(totals)

    a = totals[0]

    colSize = len(a[0])

    

    countArray = np.zeros((rowSize + 1,colSize)) # array with columns as shapefile features & rows as ranks

    nullArray = np.zeros((rowSize + 1,colSize)) # array with columns as shapefile features & rows as ranks

    #loop through and get out counts and nulls for each feature (region / district)

    for i in range(len(totals)):

        aa = totals[i]

        for ii in range(len(aa)):

            counts = aa[1]

            nulls = aa[2]

            for iii in range(len(counts)):

                countArray[i,iii] = counts[iii]

                nullArray[i,iii] = nulls[iii]

    # loop though array and sum up counts and arrays for each district

    #pdb.set_trace()

    countArray[10,:] = nulls # note: this bit add the null count to the end of the array

    countSums = []

          
    for i in range(colSize):

        countSums.append(np.sum(countArray[:,i]))

       
    
    
   
    #area calculations

   # pdb.set_trace()

    countSqm = countArray * 900

    countSqKm = countSqm / 1000000

    

    #proportions
    countDivision = countArray / countSums

    countProportion = countDivision * 100

  

    return countSqKm, countProportion







def plotting(countSqKm,countProportion,fieldVals):


    #loop through each district and plot
    
    size = countSqKm.shape

    

        
    for i in range(size[1]):

           

        countProps = countProportion[:,i]

        lowest = countProps[0]

        vmba = countProps[1]

        ba = countProps[2]

        av = countProps[3:7]

        av = np.sum(av)

        abv = countProps[7]

        vmaa = countProps[8]

        highest = countProps[9]

        nulls = countProps[10]

        #figure(1, figsize=(5,5))
        
        #ax = axes([0.1, 0.1, 0.8, 0.8])
          
        explode=(0.05,0.05,0.05,0.05,0.05,0.05,0.05)

        catergories = [lowest,vmba,ba,av,abv,vmaa,highest]

         
        matplotlib.rcParams.update({'font.size': 10}) 

        labels = ['Lowest '+ str(round(lowest,1))+ '%','Very much below average '+ str(round(vmba,1)) + '%','Below average '+ str(round(ba,1))+ '%','Average '+ str(round(av,1)) + '%',
                 'Above average '+ str(round(abv,1)) + '%', 'Very much above average '+ str(round(vmaa,1)) + '%', 'Highest '+ str(round(highest,1)) + '%']

        theGrid = GridSpec(1,1)

        colours = ['red','orange','yellow','lightgray','lime','darkgreen','blue']

        plt.subplot(theGrid[0, 0], aspect=1)

        
        plt.subplots_adjust(left=0.05, right=0.85) 

        #pdb.set_trace()

        plt.pie(catergories, labels=labels, colors = colours, explode = explode)

        
        #pdb.set_trace()

        plt.savefig(fieldVals[i] + '.png', dpi = 600)

    #pdb.set_trace()
        

def getShapeNames(filename,fieldname):


    #pdb.set_trace()
    
    daShapefile = filename

    driver = ogr.GetDriverByName('ESRI Shapefile')

    dataSource = driver.Open(daShapefile, 0) # 0 means read-only. 1 means writeable.

    layer = dataSource.GetLayer()

    feature = layer.GetNextFeature()

    fieldVals = []

    while feature:

      fieldVals.append(feature.GetFieldAsString(fieldname))

      feature = layer.GetNextFeature()

    return fieldVals





def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    #fieldVals = getShapeNames(cmdargs.inputVector,cmdargs.fieldName)

    results = doCounts(cmdargs.inputImage, cmdargs.inputVector, cmdargs.uid)

    #pdb.set_trace()

    fileName = cmdargs.outputfile

    sendToOutput(results,fileName)

    totals = doTotals(results)
 
    countSqKm,countProportion = doCalcs(totals)

    fieldVals = getShapeNames(cmdargs.inputVector,cmdargs.fieldName)

    plotting(countSqKm,countProportion,fieldVals)

    



        
if __name__ == "__main__":
    mainRoutine()