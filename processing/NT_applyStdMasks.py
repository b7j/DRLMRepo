#!/usr/bin/env python
'''

quick script to apply std masks to imagery

'''
import argparse
import glob
import csv
import qvf
import datetime
import numpy as np

def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--imagelist", help="List of imagery to process")


    cmdargs = p.parse_args()
    
    if cmdargs.imagelist is None:

        p.print_help()

        sys.exit()

    return cmdargs



#main function
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    imagepath = cmdargs.imagelist #get the image path from the get cmd

    pattern = "*_%sm?.img" % cmdargs.instage # create a file stage pattern to search for.

    newpattern = imagepath + pattern # add the image path the pattern

    filelist = glob.glob(newpattern)# filter the image directory for the chosen stage
      
    filelist.sort(key=lambda x: x.split("_", 2)[-1]) # sort the filtered list on image date.

    for filename in filelist: # loop through the stack of images

        stdmasked = qvf.changeoptionfield(filename, 'z', 'stdmasks') # changesone of the options in the standard mask call
       
        cmd = "qv_applystdmasks.py --infile %s --outfile %s" % (filename, stdmasked) # call the standard mask
        
        os.system(cmd) #call it




        
if __name__ == "__main__":
    mainRoutine()