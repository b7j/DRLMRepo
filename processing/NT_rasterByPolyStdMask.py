#!/usr/bin/env python
"""
Created on Wed Nov  6 12:26:37 2013

@author: stabeng 

Loop to run stdmask and qv_rastbypoly.py

generates a list of statistics for imagery based on the polygon vector shapefile

"""
import sys
import os
import argparse
import glob
import csv
import qvf
import datetime

def getCmdargs():
    p = argparse.ArgumentParser()
    p.add_argument("--instage", help="Stage to process")
    p.add_argument("--imagelist", help="List of imagery to process")
    p.add_argument("--vector", help="Vector data for zonal stats")
    p.add_argument("--uid", help="unique id field for zonal stats (id field must start with 1..)")
    p.add_argument("--out", help="name of csv file containing results of the zonal stats")
    cmdargs = p.parse_args()
    
    if cmdargs.instage is None:
        p.print_help()
        sys.exit()
    return cmdargs
    

def mainRoutine():
    cmdargs = getCmdargs()
    imagepath = cmdargs.imagelist
    pattern = "*_%sm?.img" % cmdargs.instage
    newpattern = imagepath + pattern
    filelist = glob.glob(newpattern)
    
    outputlist = []
    imname = []
    imdate = []
    header = []
    listsize = len(filelist)

    counter = 0
    for filename in filelist:
        counter += 1
        stdmasked = qvf.changeoptionfield(filename, 'z', 'stdmasks')
        cmd = "qv_applystdmasks.py --infile %s --outfile %s" % (filename, stdmasked)
        print cmd
        os.system(cmd)

        
        csvfile = "temp.csv"
        cmd = "qv_rastbypoly.py -r %s -v %s -c %s -o %s --doheadings --stats count,nullcount,min,max,mean,stddev" % (stdmasked, cmdargs.vector, cmdargs.uid, csvfile)
        print cmd
        os.system(cmd)

       
        infile = open(csvfile, "rb") 
        reader = csv.reader(infile) 
        head = []
        
        iteration = 0  
        for row in reader: 
            #row = str(row)
            
            #print row
            iteration += 1
            if iteration == 1:
               head.append(row)
            elif iteration > 2: 
                 #newline = row + "," + filename[-34:] + "," + filename[-18:-10]
                 a = filename[-34:],
                 b = filename[-18:-10]
                 year = b[0:4]
                 month = b[4:6]
                 day = b[6:]
                 date = datetime.datetime(year,month,day)
                 outputlist.append(row)
                 imname.append(a)
                 imdate.append(date)
                 


        infile.close()
        if counter == listsize:
           header.append(head)  
        
    
        #convert datetime objects to matplotlib objects

        mplDates = 


    




























    # otuput to text files
    out = open(cmdargs.out,"w")
    wr = csv.writer(out)
    #outputlist.insert(0,header)
    for item in outputlist:
        #output = str(item) + "\n"
        wr.writerow(item)


    out = open("header.csv","w")
    wr = csv.writer(out)  
    wr.writerow(header)


    out = open("imname.csv","w")
    wr = csv.writer(out)  
    wr.writerow(imname)
    
    out = open("imdate.csv","w")
    wr = csv.writer(out)  
    wr.writerow(imdate)   

if __name__ == "__main__":
    mainRoutine()