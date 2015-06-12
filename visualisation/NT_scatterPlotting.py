#!/usr/bin/env python


# get all the imports
import sys
import os
import argparse
import glob
import csv
import qvf
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import pdb
from scipy.stats import linregress




#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputcsv", help="Input csv file from timetrace tool")

    cmdargs = p.parse_args()
    
    if cmdargs.inputcsv is None:

        p.print_help()

        sys.exit()

    return cmdargs

 
def siteDetailsDictionary(filename):
	
	#pdb.set_trace()
	
	
	reader = csv.DictReader(open(filename))

	result = {}
	
	for row in reader:
		
		for column, value in row.iteritems():
			
			result.setdefault(column, []).append(value)
		
	return result


def doPlot(obs,pred):
	
	
	# fit with np.polyfit
	m, b = np.polyfit(obs, pred, 1)

	plt.plot(obs, pred, '.')
	
	plt.plot(obs, m*obs + b, '-')

def doRegression(obs,pred):
	
	stats = linregress(obs,pred)
	
	return stats
	
    
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    result = siteDetailsDictionary(cmdargs.inputcsv)

    date = result['date']
    
    siteID = result['siteID']
    
    bareRes = np.array(result['bare'])- np.array(result['b1avg'])
    
    pvRes = np.array(result['pV1'])- np.array(result['b2avg'])
    
    npvRes = np.array(result['npV1'])- np.array(result['b3avg'])
    
    dateDif = result['imDate_fldDate_Diff']
    
    bareRegress = doRegression(np.array(result['bare']),np.array(result['b1avg']))
    
    pVRegress = doRegression(np.array(result['pV1']),np.array(result['b2avg']))
    
    npVRegress = doRegression(np.array(result['npV1']),np.array(result['b3avg']))
    
    
    
   
    
    
    
    
    
    
        
        
if __name__ == "__main__":
    mainRoutine()

