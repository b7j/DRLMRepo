#!/usr/bin/env python
"""
Script to calculate the average distance from peak to trough in timetrace of npv cover 

"""
import argparse

from rios import applier

import pdb

import numpy as np

import time

#function to get cmd line inputs
def getCmdargs():
    p = argparse.ArgumentParser()
    p.add_argument("--inFrac", help="input file")
    p.add_argument("--inDecile", help ="input Decile")
    p.add_argument("--outfile", help="output")
    cmdargs = p.parse_args()
    if cmdargs.inFrac is None:
        p.print_help()
        sys.exit()

    return cmdargs



def main():
    """
    Main routine
    """
    cmdargs = getCmdargs()
    
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
        
    controls = applier.ApplierControls()
    controls.setOutputDriverName('GTiff')
    options = ['COMPRESS=LZW', 'BIGTIFF=YES', 'TILED=YES', 'INTERLEAVE=BAND', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256']
    controls.setCreationOptions(options)                                      
    controls.setWindowXsize(256) #set the rios block size to match the tiff tile size
    controls.setWindowYsize(256)

    infiles.inFrac = cmdargs.inFrac
    infiles.inDec = cmdargs.inDecile
    outfiles.comp = cmdargs.outfile
    #controls.setStatsIgnore(-110,imagename='comp')
    
    applier.apply(doAnalysis, infiles, outfiles, controls=controls)
    
# function to do the drill down through the image stack 
def doAnalysis(info, inputs, outputs):

    #pdb.set_trace()
        
    frac = np.array(inputs.inFrac)
    
    pv = np.array(inputs.inFrac[1])
    
    npv = np.array(inputs.inFrac[2])
    
    totalGc = (pv + npv)-200 #okay
    
    bare = np.array(inputs.inFrac[0])-100 #okay
    
    decileTgc = np.array(inputs.inDec[0])*10
    
    #decileBare = (np.array(abs(inputs.inDec[0])-10))
    #pdb.set_trace()
    
    decile = np.array(inputs.inDec[0])
    
    decile = decile.astype(np.float)
    
    decileBare = np.array(abs(decile-10))
    
    decileBare = decileBare * 10
        
    decileBare = decileBare.astype(np.int8)
    
    output = np.array([bare,totalGc,decileTgc,decileBare])

    outputs.comp = output #write to output array
   
  


if __name__ == "__main__":
    main()
