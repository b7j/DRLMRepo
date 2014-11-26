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




#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputcsv", help="Input csv file from timetrace tool")

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

    mplDates = mpl.dates.date2num(args[0])#convert datetime objects to matplotlib objects

    fig, ax = plt.subplots() # create a subplot object
    
    #fit a moving average

    if len(args) > 3:

        bareMov = movingaverage(args[1],4)

        greenMov = movingaverage(args[2],4)
    
        brownMov = movingaverage(args[3],4)
    
        #Do plotting

        ax.plot_date(mplDates, bareMov, linestyle = '-', color = 'red', label = 'Bare ground', markersize =  0, markeredgecolor = 'red', linewidth = 2)

        ax.plot_date(mplDates, greenMov, linestyle = '-', color = 'green', label = 'Green', markersize =  0, markeredgecolor = 'green', linewidth = 2)

        ax.plot_date(mplDates, brownMov, linestyle = '-', color = 'yellow', label = 'Brown', markersize =  0, markeredgecolor = 'green', linewidth = 2)

    elif len(args) ==  3:

        fpcMov = movingaverage(args[1],4)

        ax.plot_date(mplDates, fpcMov, linestyle = '-', color = 'green', label = 'FPC', markersize =  0, markeredgecolor = 'green', linewidth = 2)
        

    dateFmt = mpl.dates.DateFormatter('%Y-%m-%d') # set the dates to preferred format 'Year, month, day' in this case

    ax.xaxis.set_major_formatter(dateFmt) # set the axis with the preferred date format

    #ax.xaxis.set_minor_formatter(dateFmt)

    majorLoc = mpl.dates.MonthLocator(interval=24)

    minorLoc = mpl.dates.MonthLocator(interval=12)

    ax.xaxis.set_major_locator(majorLoc)

    ax.xaxis.set_minor_locator(minorLoc)

    fig.set_size_inches(18,6)

    ax.set_ylim([0,100])
    
    fig.autofmt_xdate(bottom = 0.18) # let matplotlib auto format the dates on the x axis

    plt.ylabel('Proportion (%)',fontsize = 10, fontweight = 700, color = 'black') # set the ylabel

    plt.xlabel('Date',fontsize = 10, fontweight = 700, color = 'black') # set the xlabel

    plt.legend(bbox_to_anchor=(1.18, 0.6))

    plt.subplots_adjust(left=0.05, right=0.85)

    plt.savefig(args[4] + '.png', dpi = 600)

    
def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    infile = open(cmdargs.inputcsv, "rb") # open the temp csv file

    reader = csv.reader(infile) # read the temp csv file

    iteration = 0

    objectId = []

    bareAvg = []

    greenAvg = []

    brownAvg = []

    fpcAvg = []

    imdate = []

    for row in reader:

        iteration += 1

        if iteration >= 2:

           objectId.append(row[0])

           if len(row) >= 20:

              fpc = 0

              year = int(row[27])
  
              month = int(row[28])

              day = int(row[29])

              date = datetime.datetime(year,month,day)

              imdate.append(date)
  
              bareAvg.append(float(row[5])-100) 
    
              greenAvg.append(float(row[11])-100)

              brownAvg.append(float(row[17])-100)

           elif len(row) <20:

              fpc = 1

              year = int(row[9])
  
              month = int(row[10])

              day = int(row[11])

              date = datetime.datetime(year,month,day)

              imdate.append(date)
              
              fpcAvg.append(float(row[5])-100)
              

    infile.close() # close the temp file

    #create list of unique ids from object Id list

    uniqueList = set(objectId)

    #loop through each unique value and create a plot for each item

    for item in uniqueList:

        indexes = [i for i,x in enumerate(objectId) if x == item]# get the occurences of the id in uniqueList as an index to apply back to lists

        if fpc == 0:

           bareSliced = [bareAvg[i] for i in indexes]

           greenSliced = [greenAvg[i] for i in indexes]

           brownSliced = [brownAvg[i] for i in indexes]

           imdateSliced = [imdate[i] for i in indexes]
            
           doPlot(imdateSliced,bareSliced,greenSliced,brownSliced,'TimetraceID_' + str(item))# call the doplot function

        elif fpc == 1:

           imdateSliced = [imdate[i] for i in indexes]

           fpcSliced = [fpcAvg[i] for i in indexes]

           doPlot(imdateSliced,fpcSliced,'TimetraceID_' + str(item))# call the doplot function


        
if __name__ == "__main__":
    mainRoutine()

