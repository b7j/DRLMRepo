#!/usr/bin/env python

"""
Purpose: calculates longterm 5th percentile, mean, median, 
         95th percentile, std dev and count rasters for each season 
         from seasonal data for each fraction. 
         result is 4 (season) x 3 (fraction) x 6 band rasters.
         

         Not an operational product. Outputs saved in projects under
         vegetation/groundcover/non_standard_products. Still needs to 
         be adapted for green and non-green cover if necessary. DNscaling
         should also be added.  
      
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
    outfiles.bare = qvf.changestage(qvf.changedate(os.path.basename(obs.inputImages[0]),obs.era),obs.stage)


   # outfiles.green = qvf.changestage(qvf.changedate(os.path.basename(obs.inputImages[0]),obs.era),'djm')
   # outfiles.nongreen = qvf.changestage(qvf.changedate(os.path.basename(obs.inputImages[0]),obs.era),'djn')
    obs.outfile = outfiles.bare


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

    for cover in ['bare']:
        if cover == 'bare':
            index = 0

        stack = np.array([img[index] for img in inputs.images])
        maskedstack = ma.masked_array(stack,stack==0)

        percentile5 = np.ma.apply_along_axis(mstats.scoreatpercentile,0,maskedstack,5)
        percentile50 = np.ma.apply_along_axis(mstats.scoreatpercentile,0,maskedstack,50)
        percentile95 = np.ma.apply_along_axis(mstats.scoreatpercentile,0,maskedstack,95)
        fractMean = np.ma.mean(maskedstack, axis=0)
        fractStd = np.ma.std(maskedstack, axis=0)
        fractCount = np.ma.count(maskedstack, axis=0)

    outputs.bare=np.array([percentile5,fractMean,percentile50,percentile95,fractStd,fractCount],dtype=np.uint8)





def addHistory(obs):
    """
    Add processing history
    """
    parents = obs.inputImages
    opt = {}
    opt['DESCRIPTION'] = """
        Longterm 5th (band 1), mean (band 2), median (band 3), 95th percentile (band 4) 
        std deviation (band 5) and observation count (band 6) summary product for %s bare ground created from the 
        seasonal fractional ground cover product (dix).
    """ % (obs.season)
    history.insertMetadataFilename(obs.outfile, parents, opt)

        
#-----------------------------------------------------------------------
# Cmdargs
#-----------------------------------------------------------------------

class CmdArgs:
    def __init__(self):
        parser = OptionParser()
        parser.add_option("--path",dest="path",
            help="ground cover path to run") 
        parser.add_option("--row",dest="row",
            help="ground cover row to run")
        parser.add_option("--season",dest="season",
            help="season to calculate stats for")
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
    obs.season = cmdargs.season.lower()

    if len(cmdargs.path) == 2:
        path = '0%s' % cmdargs.path
    else:
        path = cmdargs.path
    if len(cmdargs.row) == 2:
        row = '0%s' % cmdargs.row
    else:
        row = cmdargs.row

    scene = 'p%sr%s' % (path,row)


    for year in range(int(cmdargs.startYear),int(cmdargs.endYear)+1):
        if obs.season == 'summer':
            obs.stage = 'djo'
            gcSeason  = 'lztmre_%s_m%s12%s02_dixa2.img' % (scene,year-1,year)
        if obs.season == 'autumn':
            obs.stage = 'djp'
            gcSeason = 'lztmre_%s_m%s03%s05_dixa2.img' % (scene,year,year)
        if obs.season == 'winter':
            obs.stage = 'djq'
            gcSeason = 'lztmre_%s_m%s06%s08_dixa2.img' % (scene,year,year)
        if obs.season == 'spring':
            obs.stage = 'djr'
            gcSeason = 'lztmre_%s_m%s09%s11_dixa2.img' % (scene,year,year)

        for zone in [3,4,5,6]:
            if qv.existsonfilestore(qvf.changeutmzone(gcSeason,zone)):
                obs.inputImages.append(qvf.changeutmzone(gcSeason,zone))
            
    qv.recallToHere(obs.inputImages)
   
    produceTotal(obs)

    for image in obs.inputImages:
        os.remove(image)
 








