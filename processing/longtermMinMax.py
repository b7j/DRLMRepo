#!/usr/bin/env python

"""
Purpose: calculates longterm 5th and 95th percentile rasters       
         from all seasonal data for each fraction. result is 3 x 2 
         band rasters.
         
         Not an operation product. Ouput raster is stored in 
         non_standard_products folder on projects under 
         vegetation/groundcover. Still needs to be adapted for 
         green and non-green cover if desired and DNScaling applied.   
      
Author:   Rebecca Trevithick
Date:     Sept 2014

"""


#----------------------------------------------------------------
# Import Modules
#----------------------------------------------------------------

import os,sys
import qvf,qv

import numpy as np
import numpy.ma as ma
import scipy.stats.mstats as mstats

from rsc.utils import DNscaling
from rsc.utils import history

from optparse import OptionParser

import fnmatch

from rios import applier, fileinfo

class Observation(object):
    def __init__(self,filePath):
      
        self.filePath = filePath

        

#-----------------------------------------------------------------
# Functions
#-------------------------------------------------------------------


def produceTotal(obs):
    """
    Set up rios to apply images
    """
    controls = applier.ApplierControls()
    controls.setReferenceImage(obs.inputImages[0])
    controls.setOutputDriverName('HFA')

    infiles = applier.FilenameAssociations()
    infiles.images = obs.inputImages

    outfiles = applier.FilenameAssociations()

    if obs.stage == 'dix':
        if obs.fraction == 'bare':
            outStage = 'djl'
        elif obs.fraction == 'green':
            outStage = 'djm'        
        elif obs.fraction == 'dry':        
            outStage = 'djn'


    outfiles.image = qvf.changestage(qvf.changedate(os.path.basename(obs.inputImages[0]),obs.era),outStage)
    obs.outfile = outfiles.image

    otherargs = applier.OtherInputs()
    imginfo = fileinfo.ImageInfo(obs.inputImages[0])
    otherargs.coverNull = imginfo.nodataval[0]
    controls.setStatsIgnore(otherargs.coverNull)

    applier.apply(model, infiles, outfiles, otherargs, controls=controls)

    addHistory(obs)

    


def model(info, inputs, outputs, otherargs):
    """
    create image stack and statistics from bands
    """  
    np.seterr(all='ignore')
    
    nullValue  = otherargs.coverNull

    if qvf.stage(outputs.image) in ['djl']:
        index = 0
    if qvf.stage(outputs.image) in ['djm']:
        index = 1
    if qvf.stage(outputs.image) in ['djn']:
        index = 2        
        
    stack = np.array([img[index] for img in inputs.images])
    maskedstack = ma.masked_array(stack,stack==0)

    percentile5 = np.ma.apply_along_axis(mstats.scoreatpercentile,0,maskedstack,5)
    percentile95 = np.ma.apply_along_axis(mstats.scoreatpercentile,0,maskedstack,95)

    outputs.bare=np.array([percentile5,percentile95],dtype=np.uint8)





def addHistory(obs):
    """
    Add processing history
    """
    parents = obs.inputImages
    opt = {}
    opt['DESCRIPTION'] = """
        Longterm 5th and 95th percentile summary product for the %s fraction
        created from the %s product for all available 
        data on record from the start of summer (1st Dec) %s until the end of 
        the spring season (31 Nov) in %s .
    """ % (obs.fraction,obs.stage,obs.startYear,obs.endYear)
    history.insertMetadataFilename(obs.outfile, parents, opt)

        
#-----------------------------------------------------------------------
# Cmdargs
#-----------------------------------------------------------------------

class CmdArgs:
    def __init__(self):
        parser = OptionParser()
        parser.add_option("--path",dest="path",
            help="path to run") 
        parser.add_option("--row",dest="row",
            help="row to run")
        parser.add_option("--stage",dest="stage",
            help="stage to run")            
        parser.add_option("--fraction",dest="fraction",
            help="fraction to run. 'green','dry' or 'bare'")             
        parser.add_option("--startYear",dest="startYear",
            help="starting year for annual image (includes the summer of the year before - starting 1 Dec).")
        parser.add_option("--endYear",dest="endYear",
            help="ending year for annual image (ends Nov 31 of specified year)")
        (options, args) = parser.parse_args()
        self.__dict__.update(options.__dict__)

#-----------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------

if __name__ == "__main__":
    cmdargs=CmdArgs()

    obs = Observation('.')
    obs.inputImages = []
    obs.era = 'e%s%s' % (cmdargs.startYear[-2:],cmdargs.endYear[-2:])
    obs.stage = cmdargs.stage
    obs.fraction = cmdargs.fraction
    obs.startYear = cmdargs.startYear
    obs.endYear = obs.endYear    

    if len(cmdargs.path) == 2:
        path = '0%s' % cmdargs.path
    else:
        path = cmdargs.path
    if len(cmdargs.row) == 2:
        row = '0%s' % cmdargs.row
    else:
        row = cmdargs.row

    print path,row
    scene = 'p%sr%s' % (path,row)
    print scene 

    for year in range(int(cmdargs.startYear),int(cmdargs.endYear)+1):
        gcSummer = 'lztmre_%s_m%s12%s02_%sa2.img' % (scene,year-1,year,obs.stage)
        gcAutumn = 'lztmre_%s_m%s03%s05_%sa2.img' % (scene,year,year,obs.stage)
        gcWinter = 'lztmre_%s_m%s06%s08_%sa2.img' % (scene,year,year,obs.stage)
        gcSpring = 'lztmre_%s_m%s09%s11_%sa2.img' % (scene,year,year,obs.stage)

        for zone in [3,4,5,6]:
            if qv.existsonfilestore(qvf.changeutmzone(gcSummer,zone)):
                obs.inputImages.append(qvf.changeutmzone(gcSummer,zone))
            if qv.existsonfilestore(qvf.changeutmzone(gcAutumn,zone)):
                obs.inputImages.append(qvf.changeutmzone(gcAutumn,zone))
            if qv.existsonfilestore(qvf.changeutmzone(gcWinter,zone)):
                obs.inputImages.append(qvf.changeutmzone(gcWinter,zone))
            if qv.existsonfilestore(qvf.changeutmzone(gcSpring,zone)):
                obs.inputImages.append(qvf.changeutmzone(gcSpring,zone))

    qv.recallToHere(obs.inputImages)

    produceTotal(obs)

    for image in obs.inputImages:
        os.remove(image)
 








