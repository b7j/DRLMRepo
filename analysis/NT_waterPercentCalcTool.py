#!/usr/bin/env python
"""
Calculate water count as a percentage of all observations

"""
import argparse

from rios import applier

#function to get cmd line inputs
def getCmdargs():
    p = argparse.ArgumentParser()
    p.add_argument("--infile", help="input file")
    p.add_argument("--outfile", help="output")
    cmdargs = p.parse_args()
    if cmdargs.infile is None:
        p.print_help()
        sys.exit()

    return cmdargs

PCNT_NULL = 255

def main():
    """
    Main routine
    """
    cmdargs = getCmdargs()
    
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    controls = applier.ApplierControls()
    
    infiles.counts = cmdargs.infile
    outfiles.percent = cmdargs.outfile
    controls.setStatsIgnore(PCNT_NULL)
    
    applier.apply(doPcnt, infiles, outfiles, controls=controls)
    

def doPcnt(info, inputs, outputs):
    """
    Called by RIOS. 
    Calculate percentage
    """
    wetcount = inputs.counts[0].astype(numpy.float32)
    obscount = inputs.counts[1]
    percent = (100.0 * wetcount / obscount).astype(numpy.uint8)
    outputs.percent = numpy.array([percent])
    # Set a null value in areas where denominator is zero
    outputs.percent[0][inputs.count[1] == 0] = PCNT_NULL

def readList(filelist):




if __name__ == "__main__":
    main()
