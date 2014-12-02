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
    p.add_argument("--infile", help="input file")
    p.add_argument("--outfile", help="output")
    cmdargs = p.parse_args()
    if cmdargs.infile is None:
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
    
    infiles.inimg = readList(cmdargs.infile)
    outfiles.avg = cmdargs.outfile
   
    
    applier.apply(doAnalysis, infiles, outfiles, controls=controls)
    
# function to do the drill down through the image stack 
def doAnalysis(info, inputs, outputs):

    
    print time.strftime('%X %x %Z')
    

    npv = np.array([img[2] for img in inputs.inimg])
    # At this point, npv is an array with shape (nDates, nRows, nCols)

    sizeNpv = npv.shape

    output = np.zeros((sizeNpv[1],sizeNpv[2]),float) # create a blank array the same size as the input to be written out

    #pdb.set_trace()
    (nBands, nRows, nCols) = npv.shape

    outputs.avg = np.zeros((1,nRows,nCols),float)

    for i in range(nRows):

        for j in range(nCols):

            drill = npv[:, i, j]

            if sum(drill==0) < len(drill)/2:

                maxPeak,minPeak = peakdetect(drill)
   
                if maxPeak and minPeak:

                    outputs.avg[0,i,j] = calcPeakDist(maxPeak,minPeak) 

    

    outputs.avg = np.array([output]) #write to output array
   
    

 #Function to read in list of images to pass to applier   

def readList(imageList):


    output = [line.rstrip() for line in open(imageList)]

   
    return output

#Function to smooth out noisy data with a moving average

def movingaverage(interval, window_size):

    window = np.ones(int(window_size))/float(window_size)

    return np.convolve(interval, window, 'same')

#data check function called from within peak detect to make sure input is a numpy array and to create x axis 

def _datacheck_peakdetect(x_axis, y_axis):
    if x_axis is None:
        x_axis = range(len(y_axis))
    
    if len(y_axis) != len(x_axis):
        raise (ValueError, 
                'Input vectors y_axis and x_axis must have same length')
    
    #needs to be a numpy array
    y_axis = np.array(y_axis)

    y_axis = movingaverage(y_axis,4)

    x_axis = np.array(x_axis)

    return x_axis, y_axis

#Function to find min and max peaks in drill of stack

def peakdetect(y_axis, x_axis = None, lookahead = 10, delta=0):
    """
    Converted from/based on a MATLAB script at: 
    http://billauer.co.il/peakdet.html
    
    function for detecting local maximas and minmias in a signal.
    Discovers peaks by searching for values which are surrounded by lower
    or larger values for maximas and minimas respectively
    
    keyword arguments:
    y_axis -- A list containg the signal over which to find peaks
    x_axis -- (optional) A x-axis whose values correspond to the y_axis list
        and is used in the return to specify the postion of the peaks. If
        omitted an index of the y_axis is used. (default: None)
    lookahead -- (optional) distance to look ahead from a peak candidate to
        determine if it is the actual peak (default: 200) 
        '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
    delta -- (optional) this specifies a minimum difference between a peak and
        the following points, before a peak may be considered a peak. Useful
        to hinder the function from picking up false peaks towards to end of
        the signal. To work well delta should be set to delta >= RMSnoise * 5.
        (default: 0)
            delta function causes a 20% decrease in speed, when omitted
            Correctly used it can double the speed of the function
    
    return -- two lists [max_peaks, min_peaks] containing the positive and
        negative peaks respectively. Each cell of the lists contains a tupple
        of: (position, peak_value) 
        to get the average peak value do: np.mean(max_peaks, 0)[1] on the
        results to unpack one of the lists into x, y coordinates do: 
        x, y = zip(*tab)
    """
    max_peaks = []
    min_peaks = []
    dump = []   #Used to pop the first hit which almost always is false
       
    # check input data
    x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
    # store data length for later use
    length = len(y_axis)
    
    
    #perform some checks
    if lookahead < 1:
        raise ValueError, "Lookahead must be '1' or above in value"
    if not (np.isscalar(delta) and delta >= 0):
        raise ValueError, "delta must be a positive number"
    
    #maxima and minima candidates are temporarily stored in
    #mx and mn respectively
    mn, mx = np.Inf, -np.Inf
    

    #pdb.set_trace()
    #Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead], y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x
        
        ####look for max####
        if y < mx-delta and mx != np.Inf:
            #Maxima peak candidate found
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].max() < mx:
                max_peaks.append([mxpos, mx])
                dump.append(True)
                #set algorithm to only find minima now
                mx = np.Inf
                mn = np.Inf
                if index+lookahead >= length:
                    #end is within lookahead no more peaks can be found
                    break
                continue
            #else:  #slows shit down this does
            #    mx = ahead
            #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
        
        ####look for min####
        if y > mn+delta and mn != -np.Inf:
            #Minima peak candidate found 
            #look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].min() > mn:
                min_peaks.append([mnpos, mn])
                dump.append(False)
                #set algorithm to only find maxima now
                mn = -np.Inf
                mx = -np.Inf
                if index+lookahead >= length:
                    #end is within lookahead no more peaks can be found
                    break
            #else:  #slows shit down this does
            #    mn = ahead
            #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]
    
    
    #Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            max_peaks.pop(0)
        else:
            min_peaks.pop(0)
        del dump
    except IndexError:
        #no peaks were found, should the function return empty lists?
        pass
        
    return [max_peaks, min_peaks]

#Function to calcualte the average distance from the major peaks to troughs from each drill / timetrace

def calcPeakDist(maxPeak,minPeak):

    #differences

    #first match up lists of max and mins in the case of an uneven number of maxs and mins (occurs when last min in trace is not calculated)

    maxSize = len(maxPeak)

    #print str(maxSize)

    minSize = len(minPeak)

    #print str(minSize)

    dif = maxSize - minSize

    #pdb.set_trace()

    if dif > 0 :

       maxPeak = maxPeak[0:minSize]

    if dif < 0 :

       minPeak = minPeak[0:maxSize]


    difference = np.array(minPeak) - np.array(maxPeak)

    

     #calculate the average number of steps between the peaks and troughs for the entire time trace

    posAvg = sum(difference[:,0])/ len(maxPeak)

    return posAvg


if __name__ == "__main__":
    main()
