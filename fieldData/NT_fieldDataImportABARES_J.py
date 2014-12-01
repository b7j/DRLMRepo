#!/usr/bin/env python

'''
This is a a scrit to import data from ipad 'Rangelands proforma' asat december 2013.
Note: this version loops through a directory containing xls files and outputs in one txt file one of the many versions of the transect sheet!!!!

'''
import xlrd

import argparse

import pdb

import math

import csv

import glob

import numpy as np




#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--transInputdir", help="Input directory containing transect xl data")

    p.add_argument("--siteInputdir", help="Input directory containing xl files from ipad")

    p.add_argument("--outputfile", help="output txt file")

    cmdargs = p.parse_args()
    
    if cmdargs.transInputdir is None:

        p.print_help()

        sys.exit()

    return cmdargs


def utmToLatLng(zone, easting, northing, northernHemisphere=False):
    if not northernHemisphere:
        northing = 10000000 - northing

    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))

    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

    if not northernHemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

    return (latitude, longitude)



def getSiteDetails(siteDetails,workbook):

    #pdb.set_trace()

    centrePointEasting = float(siteDetails.cell_value(1,11))
     
    centrePointNorthing = float(siteDetails.cell_value(1,12))
    
    UTMzone = siteDetails.cell_value(1,7)
    
    date = siteDetails.cell_value(1,3)

    print str(date)
  

    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(date, workbook.datemode)

    #pdb.set_trace()
    
    date = str(day)+'/'+str(month)+'/'+str(year)
    
    observer = siteDetails.cell_value(1,9)
    
    recorder = siteDetails.cell_value(1,9)
    
    siteid = siteDetails.cell_value(1,2)

    latitude, longitude = utmToLatLng(UTMzone, centrePointEasting, centrePointNorthing)

    return (latitude, longitude, date, observer, recorder, siteid) 

 


def gettransectdata(tdata):

       
    crust = tdata.col_values(1,2,302)

    dist = tdata.col_values(2,2,302)

    rock = tdata.col_values(3,2,302)

    greenleaf = tdata.col_values(4,2,302)

    deadleaf = tdata.col_values(5,2,302)

    litter = tdata.col_values(6,2,302)

    crypto = tdata.col_values(7,2,302)

    mGl = tdata.col_values(9,2,302)

    mDl = tdata.col_values(10,2,302)

    mB = tdata.col_values(11,2,302)

    iC = tdata.col_values(13,2,302)

    uGl = tdata.col_values(14,2,302)

    uDl = tdata.col_values(15,2,302)

    uB = tdata.col_values(16,2,302)

    #pdb.set_trace() 


    output = []

 

    for i in range(len(crust)):

        

        if crust[i] == 1:

            ground = 'crust'

        elif dist[i] == 1:

            ground = 'disturbed'

        elif rock[i] == 1:

            ground = 'rock'

        elif greenleaf[i] == 1:

            ground = 'green leaf'

        elif deadleaf[i] == 1:

            ground = 'dead leaf'

        elif litter[i] == 1:

            ground = 'litter'

        elif crypto[i] == 1:

            ground = 'cryptogram'

        #pdb.set_trace()

        if mGl[i] == 1:

            mid = 'mid green leaf'

        elif mDl[i] == 1:

            mid = 'mid dead leaf'

        elif mB[i] == 1:

            mid = ' mid branch'

        elif mGl[i] == 0 or not mGl[i] == True and mDl[i] == 0 or not mDl[i] == True and mB[i] == 0 or not mB[i] == True:

            mid = 'BLANK'

        if iC[i] == 1:

            upp = 'in crown'

        elif uGl[i] == 1:

            upp = 'upper green leaf'

        elif uDl[i] == 1:

            upp = 'upper dead leaf'

        elif uB[i] == 1:

            upp = 'upper branch'

        elif iC[i] == 0 or not iC[i] == True and uGl[i] == 0 or not uGl[i] == True and uDl[i] == 0 or not uDl[i] == True and uB[i] == 0 or not uB[i] == True:

            upp = 'BLANK'

        output.append(ground + ',' + mid + ',' + upp)
  
    

    return (output)

def sendToOutput(lat,longt,date,siteID,observer,recorder,transectID,data):

    #pdb.set_trace()

    header = str(lat) + ';' + str(longt) + ';' + date + ';' + siteID + ';' + observer + ';' + recorder + ';' + transectID + ';'
        

    dataJoined = ";".join(data)

    headerString = header.encode('utf8')

    out = headerString + dataJoined
   
    return (out)
    

def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    

    transDirectory = cmdargs.transInputdir
    
    pattern = "%s/*.xls" % transDirectory # create a file stage pattern to search for.

    transFilelist = glob.glob(pattern)# filter the image directory for the chosen stage

    transFilelist.sort(key=lambda x: x.split("_", 2)[-1]) # sort the filtered list on filename

    

    siteDirectory = cmdargs.siteInputdir    

    pattern = "%s/*.xls" % siteDirectory # create a file stage pattern to search for.

    siteFilelist = glob.glob(pattern)# filter the image directory for the chosen stage

    siteFilelist.sort(key=lambda x: x.split("_", 2)[-1]) # sort the filtered list on filename

    

    output = []

    #pdb.set_trace()

    for i in range(len(siteFilelist)):

          print siteFilelist[i]

          print transFilelist[i]

          #pdb.set_trace()

          siteWorkbook = xlrd.open_workbook(siteFilelist[i])

          siteWorksheets = siteWorkbook.sheet_names()

          siteDetailSheet = siteWorkbook.sheet_by_name(siteWorksheets[4])

          
          transWorkbook = xlrd.open_workbook(transFilelist[i])


          transWorksheets = transWorkbook.sheet_names()

          transectDetails = transWorkbook.sheet_by_name(transWorksheets[0])

                    
          #transectDetails = workbook.sheet_by_name(worksheets[0])

          #pdb.set_trace()

          latitude, longitude, date, observer, recorder, siteid = getSiteDetails(siteDetailSheet,siteWorkbook)

          

          transectData = gettransectdata(transectDetails)

          t1 = transectData[0:100] 

          print len(t1)

          t2 = transectData[100:200]

          print len(t2)

          t3 =transectData[200:300]

          print len(t3)

          #pdb.set_trace()

          a = 'Transect 1'

          b = 'Transect 2'

          c = 'Transect 3'

          northSouth = sendToOutput(latitude,longitude,date,siteid,observer,recorder,a,t1)

          output.append(northSouth)

          southEast = sendToOutput(latitude,longitude,date,siteid,observer,recorder,b,t2)
          
          output.append(southEast)

          northEast = sendToOutput(latitude,longitude,date,siteid,observer,recorder,c,t3)
          
          output.append(northEast)

    files = open(cmdargs.outputfile, "w")

    for i in output:
        
        files.write(i + '\n')

    files.close()

if __name__ == "__main__":
    mainRoutine()