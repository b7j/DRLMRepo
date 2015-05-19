#!/usr/bin/env python
"""
Created on Wed Nov  6 12:26:37 2013

@author: Barnetson 

Loop to run stdmask and qv_rastbypoly.py

generates a list of statistics for imagery based on the polygon vector shapefile

Note: modified to include graphing function, works at this stage on only one polygon at a time, will code to include multiple polygons at another stage

Need to add a trend curve, tested with polyft and interpolate, needs more work, check this http://stackoverflow.com/questions/6939901/average-trend-curve-for-data-points-in-python

for a worked example


"""

# get all the imports
import sys
import os
import argparse
import glob
import csv
import qvf
import datetime
import numpy as np
import pdb



#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--instage", help="Stage to process")

    p.add_argument("--imagelist", help="List of imagery to process")
    
    p.add_argument("--imagepath", help="Path to imagery")

    p.add_argument("--vector", help="Vector data for zonal stats")

    p.add_argument("--uid", help="unique id field for zonal stats (id field must start with 1..)")

    p.add_argument("--csv", help="Name of output csv file")

    cmdargs = p.parse_args()
    
    if cmdargs.instage is None:

        p.print_help()

        sys.exit()

    return cmdargs

#function to export data
def exportData(data,outputName):

    w = csv.writer(file(outputName, 'wb'), dialect = 'excel') #create csv file

    w.writerows(data) #write to file
  

#main function
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    imagelist = cmdargs.imagelist #get the image path from the get cmd
    
    filelist = []
    
    with open(imagelist, "r") as ifile:
	
	for line in ifile:
		
		#pdb.set_trace()
		
		lineA = line.rstrip()
		
		lineB = lineA.strip('\n')
		
		path = cmdargs.imagepath + lineB
		
		filelist.append(path)
		
		
	

    #pdb.set_trace()
    
    filelist.sort(key=lambda x: x.split("_", 2)[-1]) # sort the filtered list on image date.

    
    
    #setup some output lists

    

    outputlist = []

    imdate = []

    objectId = []

    bareAvg = []

    bareStdDev = []

    greenAvg = []

    greenStdDev = []

    brownAvg = []

    brownStdDev = []

    fpcAvg = []

    counter = 0 # image counter
         

    for filename in filelist: # loop through the stack of images

        counter += 1 # add one to the counter

        
	
	#filename = filename[-33:]

        print str(counter) + ' of ' + str(len(filelist)) # print the counter 

        csvfile = "temp.csv" 

        imagename = filename[-34:] 

        season = filename[-22:-10]
	
	#pdb.set_trace()

        cmd = "qv_rastbypoly.py -r %s -v %s -c %s -o %s --doheadings --stats count,nullcount,min,max,mean,stddev" % (filename, cmdargs.vector, cmdargs.uid, csvfile) # call raster by poly

        os.system(cmd) # call it
        
            #pdb.set_trace()
        
        infile = open(csvfile, "rb") # open the temp csv file

        reader = csv.reader(infile) # read the temp csv file

        iteration = 0 

        #pdb.set_trace()
 
        for row in reader: # loop through the temp csv file
            
            iteration += 1

            
            #print row 

            #print str(iteration)

            if iteration == 1 and counter == 1: #test to get the header row of the csv file for the output csv

                row.append('imageName')

                row.append('season')
                
                outputlist.append(row) # append to the output list
            
            none = row[3:4]


            if 'None' in none: # test to check if any nulls in row list

                nulls = 1
            
            else:

                nulls = 0

            if iteration > 1 and nulls == 0: # test to skip over header row and ignore any rows with nulls
                 
                 #print row # print the output row, puerly for testing things are working

                 # next few lines decomposes the filename to get the image date for plotting

                 #print str(nulls)
                                

                 row.append(imagename) #append date to end of row

                 row.append(season) #append image name to end of row

                 outputlist.append(row) # append to the output list for csv output.

                 #imdate.append(date)

                 objectId.append(row[0])
                
                                    
                  
        infile.close() # close the temp file
    
    
    exportData(outputlist,cmdargs.csv)#write data out to a excel csv file

        
if __name__ == "__main__":
    mainRoutine()