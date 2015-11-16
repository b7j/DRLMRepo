#!/usr/bin/env python


import sys
import os
import argparse
import numpy as np
from scipy.spatial.distance import cdist
import pdb
import osr
import pandas

#...............................................................................

metric = "euclidean"


#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputCsv", help="Input csv file from timetrace tool")
    
    p.add_argument("--outputCsv", help="output file")
    
    #p.add_argument("--outputcsv", help="Output csv file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputCsv is None:

        p.print_help()

        sys.exit()

    return cmdargs
    
def transform_wgs84_to_utm(lon, lat):   
	 
    def get_utm_zone(longitude):
	    
        return (int(1+(longitude+180.0)/6.0))

    def is_northern(latitude):
        """
        Determines if given latitude is a northern for UTM
        """
        if (latitude < 0.0):
		
            return 0
	
        else:
		
            return 1

    utm_coordinate_system = osr.SpatialReference()
    
    utm_coordinate_system.SetWellKnownGeogCS("WGS84")
     # Set geographic coordinate system to handle lat/lon  
    utm_coordinate_system.SetUTM(get_utm_zone(lon), is_northern(lat))

    wgs84_coordinate_system = utm_coordinate_system.CloneGeogCS() # Clone ONLY the geographic coordinate system 

    # create transform component
    wgs84_to_utm_transform = osr.CoordinateTransformation(wgs84_coordinate_system, utm_coordinate_system) # (<from>, <to>)
    return wgs84_to_utm_transform.TransformPoint(lon, lat, 0) # returns easting, northing, altitude  



def doDistance(matrix):
	
	myArray = []
		
	for i in range(len(matrix)):
		
		a = matrix[i]
		
		aa = a[0]
		
		bb = a[1]
		
		cc = transform_wgs84_to_utm(aa, bb)
		
		#pdb.set_trace()
			
		coords = np.array(cc[0:2])
					
		myArray.append(coords)
		
	coordArray = np.array(myArray)
	
	#pdb.set_trace()
		
	dist = cdist( coordArray, coordArray, metric=metric )  # -> (nx, ny) distances
	
	dia = np.diag_indices(len(coordArray))
	
	dist[dia] = 'NAN'
	
	minimum = np.nanmin(dist)
	
	mins = minimum / 1000
	
	maximum = np.nanmax(dist)
	
	maxs = maximum / 1000
	
	#pdb.set_trace()

	return maxs, mins

def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function        

    # open the spreadsheet with transect data

    df = pandas.read_csv(cmdargs.inputCsv,header=0)
    
    property = df.property
    
    uniqueProps = property.unique()
    
    allValues = {'property':[],'mins':[],'maxs':[]}
    
    for i in uniqueProps:
	    
	print i
	
				    
	sliced = df[df['property'].str.contains(i)]
	
	sLat = sliced['lat'].values.tolist()
	
	#sLat = set(sLat)
	
	#sLat = list(sLat)
	
	sLong = sliced['longt'].values.tolist()
	
	#sLong = set(sLong)
	
	#sLong = list(sLong)
	
	#pdb.set_trace()
	
	matrix = np.column_stack((sLong,sLat))
	
	uMatrix = np.array(list(set(tuple(p) for p in matrix)))
	
	maximum, minimum = doDistance(uMatrix)
	
    	allValues['property'].append(i)
	
	allValues['mins'].append(minimum)
	
	allValues['maxs'].append(maximum)
    
    
    #pdb.set_trace()    
    
    fileName = cmdargs.outputCsv
    
    df = pandas.DataFrame(allValues)
    
    df.to_csv(fileName)
    
        
if __name__ == "__main__":
    mainRoutine()
