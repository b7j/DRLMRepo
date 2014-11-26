#!/usr/bin/env python

'''
This is a a scrit to import data from ipad 'Rangelands proforma v4.3.xls' asat June2014, prior to refit of fraction lookup to include woody regrowth as discussed in darwin june 13

'''
import xlrd

import argparse

import pdb

import math

import csv



#function to get cmd line inputs
def getCmdargs():

    p = argparse.ArgumentParser()

    p.add_argument("--inputxlfile", help="Input xl file from Ipad")

    p.add_argument("--outputfile", help="output txt file")

    cmdargs = p.parse_args()
    
    if cmdargs.inputxlfile is None:

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

    centrePointEasting = float(siteDetails.cell_value(12,1))
     
    centrePointNorthing = float(siteDetails.cell_value(13,1))
    
    UTMzone = siteDetails.cell_value(14,1)
    
    date = siteDetails.cell_value(9,1)

    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(date, workbook.datemode)

    date = str(day)+'/'+str(month)+'/'+str(year)
    
    observer = siteDetails.cell_value(4,1)
    
    recorder = siteDetails.cell_value(3,1)
    
    siteid = siteDetails.cell_value(8,1)

    latitude, longitude = utmToLatLng(UTMzone, centrePointEasting, centrePointNorthing)

    return (latitude, longitude, date, observer, recorder, siteid) 


def gettransectdata(tdata):

    gl = tdata.col_values(1,2,102)

    wd = tdata.col_values(2,2,102)

    ul = tdata.col_values(3,2,102)

    ml = tdata.col_values(4,2,102)

    #pdb.set_trace()

    return (gl, wd, ul, ml)

def sendToOutput(lat,longt,date,siteID,observer,recorder,transectID,ground,woodyDown,mid,upper):

    

    aa = str(lat) + ';' + str(longt) + ';' + date + ';' + siteID + ';' + observer + ';' + recorder + ';' + transectID + ';'
    
    transect = []

    transect.append(aa)    

     
    #pdb.set_trace()

    for i in range(len(ground)):

        a = ground[i]

        aa = a.encode('utf8') #convert from excel unicode to a string because excel is outputting as unicode

        #pdb.set_trace()
               
        b = woodyDown[i]
  
        bb = b.encode('utf8')

        c = mid[i]

        cc = c.encode('utf8')

        d = upper[i]

        dd = d.encode('utf8')
        
        transect.append(aa + ',' + bb + ',' + cc + ',' + dd)

        
    #pdb.set_trace() 

    newList = ";".join(transect)
   
    return (newList)
    

def mainRoutine():

    cmdargs = getCmdargs() # instantiate the get command line function

    aa = cmdargs.inputxlfile

    workbook = xlrd.open_workbook(aa)

    worksheets = workbook.sheet_names()

    siteDetailSheet = workbook.sheet_by_name(worksheets[0])
    
    transectNSSheet = workbook.sheet_by_name(worksheets[3])

    transectSENWSheet = workbook.sheet_by_name(worksheets[4])

    transectNESWSheet = workbook.sheet_by_name(worksheets[5])

    basalSheet = workbook.sheet_by_name(worksheets[6])

    latitude, longitude, date, observer, recorder, siteid = getSiteDetails(siteDetailSheet,workbook)

    glns, wdns, ulns, mlns = gettransectdata(transectNSSheet)

    glse, wdse, ulse, mlse = gettransectdata(transectSENWSheet)

    glne, wdne, ulne, mlne = gettransectdata(transectNESWSheet)

    #pdb.set_trace()

    output = []

    northSouth = sendToOutput(latitude,longitude,date,siteid,observer,recorder,worksheets[3],glns,wdns,mlns,ulns)

    output.append(northSouth)

    southEast = sendToOutput(latitude,longitude,date,siteid,observer,recorder,worksheets[4],glse,wdse,mlse,ulse)
    
    output.append(southEast)

    northEast = sendToOutput(latitude,longitude,date,siteid,observer,recorder,worksheets[5],glne,wdne,mlne,ulne)
    
    output.append(northEast)

    files = open(cmdargs.outputfile, "w")

    for i in output:
        
        files.write(i + '\n')

    files.close()

if __name__ == "__main__":
    mainRoutine()