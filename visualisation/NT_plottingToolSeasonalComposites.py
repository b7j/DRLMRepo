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




#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputcsv", help="Input csv file from timetrace tool")
    
    p.add_argument("--outputcsv", help="Output csv file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputcsv is None:

        p.print_help()

        sys.exit()

    return cmdargs

def movingaverage(interval, window_size):

    window = np.ones(int(window_size))/float(window_size)

    return np.convolve(interval, window, 'same')


#function to do the time trace plotting
def doPlot(*args): #note: accepts multiple inputs but must index them in the order they have been called!!

    xax = args[0]#convert datetime objects to matplotlib objects

    fig, ax = plt.subplots() # create a subplot object
    
    #fit a moving average

    '''
    bareMov = movingaverage(args[1],4)

    greenMov = movingaverage(args[2],4)
    
    brownMov = movingaverage(args[3],4)
    
    '''
    
    bareMov = args[1]

    greenMov = args[2]
    
    brownMov = args[3]
    
    z = np.polyfit(range(len(xax)), bareMov, 1)
    
    p = np.poly1d(z)
    
    x = range(len(xax))
    
    ax.plot(x,p(x),"r")
    
    z = np.polyfit(range(len(xax)), greenMov, 1)
    
    p = np.poly1d(z)
    
    x = range(len(xax))
    
    ax.plot(x,p(x),"g")
    
    z = np.polyfit(range(len(xax)), brownMov, 1)
    
    p = np.poly1d(z)
    
    x = range(len(xax))
    
    ax.plot(x,p(x),"y")
    
    
    
    
    
    
    
        #Do plotting
    

    ax.plot(bareMov, linestyle = '-', color = 'red', label = 'Bare ground', markersize =  0, markeredgecolor = 'red', linewidth = 2)

    ax.plot(greenMov, linestyle = '-', color = 'green', label = 'Green', markersize =  0, markeredgecolor = 'green', linewidth = 2)

    ax.plot(brownMov, linestyle = '-', color = 'yellow', label = 'Brown', markersize =  0, markeredgecolor = 'green', linewidth = 2)
    
    ax.set_xticks(range(len(xax)),minor = False)
    
    ax.set_xticklabels(xax,fontsize = 5,rotation = 90)
    
    

    #ax.xaxis.set_minor_locator(minorLoc)

    fig.set_size_inches(18,10)

    ax.set_ylim([0,100])
    
    

    plt.ylabel('Proportion (%)',fontsize = 10, fontweight = 700, color = 'black') # set the ylabel

    plt.xlabel('Season',fontsize = 10, fontweight = 700, color = 'black') # set the xlabel

    plt.legend(bbox_to_anchor=(1.18, 0.6))

    plt.subplots_adjust(left=0.05, right=0.85)
    
    #plt.show()
    
    #pdb.set_trace()
    
    

    plt.savefig(args[4] + '.png', dpi = 600)

def doExport(season,bare,green,brown,outfile):
	
	files = open(outfile, "w")
	
	#pdb.set_trace()
	

    	for i in range(len(season)):
		
		if i == 0:
			
			aa = 'Season,Bare,Green,Brown'
			
			files.write(aa + '\n')
		else:
		
			aa = season[i] + ',' + str(bare[i]) + ',' + str(green[i]) + ',' + str(brown[i])
        
        		files.write(aa + '\n')

    	files.close()
	
    
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    infile = open(cmdargs.inputcsv, "rb") # open the temp csv file

    reader = csv.reader(infile) # read the temp csv file
    
    

    iteration = 0

    objectId = []

    bareAvg = []

    greenAvg = []

    brownAvg = []

    season = []

    for row in reader:

        iteration += 1

        if iteration >= 2:

           objectId.append(int(row[0]))
	   
	   a = row[26]
	   
	   yearStart = int(a[0:4])
	   
	   monthStart = int(a[4:6])
	   
	   #pdb.set_trace()
	   
	   yearEnd = int(a[6:10])
	   
	   monthEnd = int(a[10:12])
	   
	   if monthStart == 9 and monthEnd == 11:
			   
	   	season.append('Spring ' + str(yearStart))
	   		
	   elif monthStart == 12 and monthEnd == 2: 
			
		season.append('Summer ' + str(yearStart) + '-' + str(yearEnd))
			
	   elif monthStart == 3 and monthEnd == 5:
			
		season.append('Autumn ' + str(yearStart))
			
	   elif monthStart == 6 and monthEnd == 8:
			
		season.append('Winter ' + str(yearStart))
			
	   
	   bareAvg.append(float(row[5])-100) 
    
           greenAvg.append(float(row[11])-100)

           brownAvg.append(float(row[17])-100)

           
              

    infile.close() # close the temp file

    #pdb.set_trace()
    
    #create list of unique ids from object Id list

    uniqueList = set(objectId)

    #loop through each unique value and create a plot for each item

    for item in uniqueList:

        indexes = [i for i,x in enumerate(objectId) if x == item]# get the occurences of the id in uniqueList as an index to apply back to lists

        bareSliced = [bareAvg[i] for i in indexes]

        greenSliced = [greenAvg[i] for i in indexes]

        brownSliced = [brownAvg[i] for i in indexes]

        seasonSliced = [season[i] for i in indexes]
            
	doExport(seasonSliced,bareSliced,greenSliced,brownSliced,'TimetraceID_' + str(item)+'.txt')    
	    
        #doPlot(seasonSliced,bareSliced,greenSliced,brownSliced,'TimetraceID_' + str(item))# call the doplot function

        
        
if __name__ == "__main__":
    mainRoutine()

