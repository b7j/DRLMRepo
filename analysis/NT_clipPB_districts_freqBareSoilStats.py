#!/usr/bin/env python

"""
Need to paste the next line to line 1 to run this script on the hpc in qld.

#!/usr/bin/env python


This script produces data requried for the annual NT annual pastoral board report. It clips out the seasonal fractional cover dim image to the extent of each NT pastoral 
districts and produces the frequency and cumulative frequency statistics for the bare ground fraction for the given season. It also outputs plots as jpg formats showing the frequency
and cumulative frequency for each pastoral district.   
 

"""

# get all the imports
import sys
import os
import argparse
import pdb
import glob
import numpy as np
from osgeo import gdal
from scipy.stats import itemfreq
import pandas as pd
import fnmatch
import matplotlib.pyplot as plt



def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inimage", help="input seasonal fractional cover image")
    
    p.add_argument("--shapes", help="list of shapefiles to clip image")
    
    p.add_argument("--directory", help="input directory")
    
    

    cmdargs = p.parse_args()
    
    if cmdargs.inimage is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
   
    
    

def doClip(inImage,shapeFiles,direct):
	
	"""
     function taken from jasons NT_clipImages.py, it clips out and produces a new raster layer for pastoral district.
     """
	
	filelist = []
    
    	with open(shapeFiles, "r") as ifile:
	
		for line in ifile:
		
		#pdb.set_trace()
	
			lineA = line.rstrip()
		
			lineB = lineA.strip('\n')
		
			filelist.append(lineB)
		
	
	for i in filelist:
     
            
		cmd = "gdalwarp -of %s -cutline %s -cl %s -crop_to_cutline %s %s" % ('GTiff',direct + i,i[0:-4],inImage,inImage[0:-4] + "_" + i[0:-4] + '.tiff') 
		
		os.system(cmd)
  

        
		


def listofFiles():
	
	"""
	this function creates a list of .tiff files that have been produced from the doClip function.
	"""
	
	# directory containing imagery to process which comes from the command line 
	direc = './'
    
    	# create empty list to store the list of csv files
    	filelist =[]
    	    
	    
    	# file pattern to search for in the directory.
    	pattern = "%s/*.tiff" % direc
	
	
	# return a list and path to files matching the pattern "tiff" in the directry 
    	file1 = glob.glob(pattern)

	# writes out the list of files  
    	for path in file1:
        	a = path[0:]
        	filelist.append(a)
		
	return filelist	
	



	

def freqStats(filelist):
	
	"""
	this function opens each .tiff image for the pastoral district in the list of files from the listofFiles function and returns the frequency stats 
    for the bare ground fraction for the imput imagery as csv file. 
	"""
	
	for i in filelist:
			
		# open the seasonal fraction image  
		image = gdal.Open(i)
		
		# read the bare soil layer, this reads the whole image into memory 
		bs = np.array(image.GetRasterBand(1).ReadAsArray())
		
		# calculate the frequency of the base soil values
		result = itemfreq(bs)
		
		# put the frequency results into a pandas data frame with column headers
		df = pd.DataFrame(result, columns = ['orig_bs', 'Count'])
	
		# creates a new column in the df and convert image bare soil values to the acutal % values
		df['bs'] = df['orig_bs'] - 100
	
		# select on the bare soil values between 0 and 100 percent -  this removes the values above and below 0-100% which are considerd noise, usaly only a very small number I hope.
		df = df[(df.bs >= 0) & (df.bs <= 100)]
	
		#creates new columns and does the calcs for cumulative frequency
		SumC = df['Count'].sum()
		df['percCount'] = (df['Count']/SumC)*100
		df['cumuPerc'] = df.percCount.cumsum()
	
		# extract the file name and remove the .tiff extention and make a new file name which includes the image and district and .csv extention to input into the pandas export to csv function
		n1 = i[2:]
		# stripts the .tiff from the image file name
		n2 = n1[:-5]		
		
		csvFileName = n2 +'_Bare_Soil_Freq.csv'	
		
		print 'Finished ' + n2
		
		# export out frequency scores to csv file
		df.to_csv(csvFileName)




def listdir(dirname, pattern="*"):

    """
    this function will return a list of csv files in a directory for the given file extention, which is input into the plot data function. 
    """
    return fnmatch.filter(os.listdir(dirname), pattern)



def plotdata(plot_filelist):
    
    for filename in plot_filelist:
        
        # read in csv file
        df = pd.read_csv(filename, header=0)# reads the csv file 
    
        print filename[:-4]
        # plot graphs
        x = df['bs']
        y = df['cumuPerc']

    
        #sets the limits of the axis
        plt.xlim(0, 100)
        plt.ylim(0, 105)
    
        """
        this code will hatch out the area under the curve defined by the cumulative percentage column        
        
        # select the area under the curve to be filled 
        df['int_cumPerc'] = df['cumuPerc'].astype(int)
        df2 = df[(df.int_cumPerc >= 80)] 
        xf = df2['bs']
        yf = df2['cumuPerc']
        
        # fill area under the curve with hatch                           
        plt.fill_between(xf, yf, color="none", alpha=1,hatch='////',edgecolor="black" )
        
        # example of a different hatch type
        #plt.fill_between([0,1],[0,1],color="none",hatch="X",edgecolor="b")
        
        """
        
        # axis labels
        plt.ylabel('Cumulative Frequency(%)')
        plt.xlabel('Percentage Bare Soil')
    
    
        # plot the cumulative frequency curve   this seems to be Garys faviroute col'firebrick'
        plt.plot(x, y, color='black')

        # save figure out with district name as the file name - the file name comes from the for loop and the extention csv is removed
        plt.savefig(filename[:-4] + '_CumulativeFreq.png', dpi=150)
        # this clears the plot and stops it from adding the previous plots data ontop of the new data
        plt.clf() 

    
    for filename in plot_filelist:
        
        # read in csv file
        df = pd.read_csv(filename, header=0)# reads the csv file 
    
        print filename[:-4]
        # plot graphs
        x = df['bs']
        y = df['percCount']

    
        #sets the limits of the axis, y axis is max value plus 0.2
        plt.xlim(0, 100)                    
        plt.ylim = df['percCount'].max() + 0.2 
   
        
        # axis labels
        plt.ylabel('Frequency(%)')
        plt.xlabel('Percentage Bare Soil')
    
    
        # plot the cumulative frequency curve   'firebrick'
        plt.plot(x, y, color='black')

        # save figure out with district name as the file name - the file name comes from the for loop and the extention csv is removed
        plt.savefig(filename[:-4] + '_Freq.png', dpi=150)
        # this clears the plot and stops it from adding the previous plots data ontop of the new data
        plt.clf()



def mainRoutine():
    
    cmdargs = getCmdargs()
    
    doClip(cmdargs.inimage,cmdargs.shapes,cmdargs.directory)
    
    filelist = listofFiles()
    
    freqStats(filelist)
    
    plot_filelist = listdir("./", "*.csv")
    
    plotdata(plot_filelist)

if __name__ == "__main__":
    mainRoutine()
    