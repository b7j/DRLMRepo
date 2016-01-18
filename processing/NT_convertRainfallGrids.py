#!/usr/bin/env python
"""
Created on Wed Nov  6 12:26:37 2013

@author: Barnetson 

This is a little script to convert all the rainfall grids to .imgs


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

    p.add_argument("--dirList", help="List of direcoties to process")
    
    p.add_argument("--dirPath", help="Path to directories")

    p.add_argument("--outputDir", help="Path to output directory")
    
    cmdargs = p.parse_args()
    
    if cmdargs.dirList is None:

        p.print_help()

        sys.exit()

    return cmdargs

#main function
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    dirList = cmdargs.dirList #get the dir path from the get cmd
    
    filelist = []
    
    with open(dirList, "r") as ifile:
	
	for line in ifile:
		
		#pdb.set_trace()
		
		lineA = line.rstrip()
		
		lineB = lineA.strip('\n')
		
		path = cmdargs.dirPath + lineB
		
		filelist.append(path)
		
		
	

    #pdb.set_trace()
    
    filelist.sort(key=lambda x: x.split("_", 2)[-1]) # sort the filtered list on image date.

    doConversion(filelist,cmdargs.outputDir)
    
    #setup some output lists

    

def doConversion(directoryList,outDir):

    for f in directoryList: # loop through the stack of images

        cmd = "find %s -name '*.mr.drr' >list.txt" % (f)
	
	os.system(cmd)
	
	images = [line.strip() for line in open("list.txt", 'r')]
	
	#pdb.set_trace()
	
	for i in images:
		
		out = i
		
		out = out[-13:-7]
		
		out = outDir + out + '.img'
		
		nodata = -1

        	cmd = "gdal_translate -of %s -a_nodata %s %s %s" % ('HFA',nodata,i,out) 

        	os.system(cmd) # call it
        
            #pdb.set_trace()
        
        
        
if __name__ == "__main__":
    mainRoutine()