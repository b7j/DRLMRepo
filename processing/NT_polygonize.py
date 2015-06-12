#!/usr/bin/env python

'''

setup some modules

'''

import pdb

import os

import argparse


'''
NOTE: need to load the following at the command line prior to running this script


"module load cgal fftw muparser rsgislib rscgeobia"

'''



def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inimageList", help="input image")
    
    p.add_argument("--directory", help="input directory")
    
    cmdargs = p.parse_args()
    
    if cmdargs.inimageList is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
   
    
    
def doPolygonize(images,directory):

	
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
		
							
		cmd  = "gdal_polygonize.py %s -f %s %s %s" % (directory + i,"ESRI Shapefile", directory + i[0:-4] + '.shp',i[0:-4])
		
		os.system(cmd) # call it
						

def mainRoutine():
	
	cmdargs = getCmdargs() # instantiate the get command line function
	
	doPolygonize(cmdargs.inimageList,cmdargs.directory)
	
	


if __name__ == "__main__":
    mainRoutine()