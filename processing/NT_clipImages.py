#!/usr/bin/env python


# get all the imports
import sys
import os
import argparse
import pdb


def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inimage", help="input image")
    
    p.add_argument("--shapes", help="list of shapefiles to clip image")
    
    p.add_argument("--directory", help="input directory")
    
    

    cmdargs = p.parse_args()
    
    if cmdargs.inimage is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
   
    
    

def doClip(inImage,shapeFiles,direct):
	
	#pdb.set_trace()
	
	filelist = []
    
    	with open(shapeFiles, "r") as ifile:
	
		for line in ifile:
		
		#pdb.set_trace()
	
			lineA = line.rstrip()
		
			lineB = lineA.strip('\n')
		
			filelist.append(lineB)
		
	
	for i in filelist:
		
		#pdb.set_trace()
				
		cmd = "gdalwarp -of %s -cutline %s -cl %s -crop_to_cutline %s %s" % ('GTiff',direct + i,i[0:-4],inImage,inImage[0:-5] + i[0:-4] + '.tiff')
		
		os.system(cmd)

def mainRoutine():
	
	cmdargs = getCmdargs() # instantiate the get command line function
	
	inputImage = cmdargs.inimage
	
	doClip(cmdargs.inimage,cmdargs.shapes,cmdargs.directory)
	
	
	


if __name__ == "__main__":
    mainRoutine()