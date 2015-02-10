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

    p.add_argument("--inimage", help="input image")
    
    

    cmdargs = p.parse_args()
    
    if cmdargs.inimage is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
   
    
    
def doSegmentation(inputImage):

	#pdb.set_trace()
				
	cmd  = "rscgeobia_segmentation.py -i %s" % (inputImage)
	
	#call raster by poly

        os.system(cmd) # call it
	
def doVectorize(infile):
	
	cmd = "gdal_polygonize.py %s %s %s" % (infile,"ESRI Shapefile",infile[0:-4]+ '.shp')
	
	os.system(cmd)

def mainRoutine():
	
	cmdargs = getCmdargs() # instantiate the get command line function
	
	inputImage = cmdargs.inimage
	
	doSegmentation(inputImage)
	
	doVectorize(inputImage)
	


if __name__ == "__main__":
    mainRoutine()