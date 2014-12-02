#!/usr/bin/env python
"""
Apply a NT fire mask to an input image
"""
import argparse

from rios import applier

from rsc.utils import gdalcommon
from rsc.utils import DNscaling

def getCmdargs():
    """
    Get commandline arguments
    """
    p = argparse.ArgumentParser()
    p.add_argument("--infile", help="Input file to be masked")
    p.add_argument("--maskfile", help="Name of fire mask file")
    p.add_argument("--outfile", help="Name of masked output image")
    cmdargs = p.parse_args()
    return cmdargs


def mainRoutine():
    """
    Main routine
    """
    cmdargs = getCmdargs()
    
    infiles = applier.FilenameAssociations()
    outfiles = applier.FilenameAssociations()
    otherargs = applier.OtherInputs()
    controls = applier.ApplierControls()
    
    infiles.inimg = cmdargs.infile
    infiles.firemask = cmdargs.maskfile
    outfiles.outimg = cmdargs.outfile
    controls.setBurnAttribute('ID')
    
    imginfo = gdalcommon.info(cmdargs.infile)
    otherargs.nullval = imginfo.nodataval[0]
    controls.setStatsIgnore(otherargs.nullval)
    
    applier.apply(doMask, infiles, outfiles, otherargs, controls=controls)
    
    DNscaling.copyDNscaling(cmdargs.infile, cmdargs.outfile)


def doMask(info, inputs, outputs, otherargs):
    """
    Called from RIOS
    """
    mask = (inputs.firemask[0] > 0)
    outputs.outimg = inputs.inimg.copy()
    nBands = len(inputs.inimg)
    for i in range(nBands):
        outputs.outimg[i][mask] = otherargs.nullval


if __name__ == "__main__":
    mainRoutine()
