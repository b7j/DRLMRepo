#!/usr/bin/env python

'''

setup some modules

'''

import pdb

import os

import argparse

import rsgislib

'''
NOTE: need to load the following at the command line prior to running this script


"module load cgal fftw muparser rsgislib rscgeobia"

'''



def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inimageList", help="input image")
    
    p.add_argument("--numclusters", help="input number of clusters def = 60")
    
    p.add_argument("--minsize", help = "input min size def = 100")
    
    p.add_argument("--filetag", help="input filetag to write to end of filename, useful for testing")
    
    p.add_argument("--directory", help="input directory")
    

    cmdargs = p.parse_args()
    
    if cmdargs.inimageList is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
   
    
    
def doSegmentation(images,numclust,minsize,tag,directory):

	
	filelist = []
    
    	with open(images, "r") as ifile:
	
		for line in ifile:
		
		#pdb.set_trace()
		
			lineA = line.rstrip()
		
			lineB = lineA.strip('\n')
		
			filelist.append(lineB)
		#pdb.set_trace()
	for i in filelist:
		
		#pdb.set_trace()
					
		cmd  = "rscgeobia_segmentation.py -i %s --numclusters %s --minsize %s --optionfield %s" % (directory + i,numclust,minsize,tag)
		
		os.system(cmd) # call it
						

def mainRoutine():
	
	cmdargs = getCmdargs() # instantiate the get command line function
	
	doSegmentation(cmdargs.inimageList,cmdargs.numclusters,cmdargs.minsize,cmdargs.filetag,cmdargs.directory)
	
	


if __name__ == "__main__":
    mainRoutine()