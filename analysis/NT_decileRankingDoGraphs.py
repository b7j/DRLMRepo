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

    p.add_argument("--inputTextFile", help="Output text from NT_decileRankingStats.py")

    p.add_argument("--inputVector", help="Input shapefile of area to be analysed")

    p.add_argument("--uid", help="Shapefile unique ID")

    p.add_argument("--outputfile", help = "output text file")

    p.add_argument("--fieldName", help = "field name in shapefile with feature names for plotting")

    cmdargs = p.parse_args()
    
    if cmdargs.inputVector is None:

        p.print_help()

        sys.exit()

    return cmdargs
 
def getTextFile(name):


     #pdb.set_trace()


     infile = open(name, "rb") 

     reader = csv.reader(infile) 

     counts = []
  
     for row in reader:

         counts.append(row)


     return counts


 

def doTotals(ranks):

    allRanks = []

    pdb.set_trace()

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
    
    size = countProportion.shape

    pdb.set_trace()

        
    for i in range(size[1]):

           

        countProps = countProportion[:,i]

        lowest = countProps[0]

        vmba = countProps[1]

        ba = countProps[2]

        av = countProps[3:6]

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

        labels = ['Lowest','Very much below average','Below average','Average', 'Above average', 'Very much above average', 'Highest']

        theGrid = GridSpec(1,1)

        colours = ['red','orange','yellow','lightgray','lime','darkgreen','blue']

        plt.subplot(theGrid[0, 0], aspect=1)

        
        plt.subplots_adjust(left=0.05, right=0.85)       

        plt.pie(catergories, labels=labels, autopct='%1.1f%%', colors = colours, explode = explode)

        #plt.show()

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

    results = getTextFile(cmdargs.inputTextFile)
    
    totals = doTotals(results)
 
    countSqKm,countProportion = doCalcs(totals)

    fieldVals = getShapeNames(cmdargs.inputVector,cmdargs.fieldName)

    plotting(countSqKm,countProportion,fieldVals)

    



        
if __name__ == "__main__":
    mainRoutine()