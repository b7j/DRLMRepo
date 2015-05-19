#!/usr/bin/env python

#a dodgy script to do a quick check of what scenes are yet to be downloaded,
#for a list of scene names (downloadScenes).
#compares the output of usgs_list_missing.py using the --state nt option
#to the scene names in the list below and writes the scenes id's we want
#to another text file specified by -o

#fiona 21/08/13


import optparse

def mainRoutine(cmdargs):             
    f = open(cmdargs.sceneList,"r")
    g = open(cmdargs.outFile,"w")
    #these are the scenes the NT guys interested in for their pilot studies
    downloadScenes = ["p102r071","p102r072","p102r073",
                    "p102r076","p102r077","p102r078",
                    "p103r071","p103r072","p103r073",
                    "p103r076","p103r077","p103r078",
                    "p104r071","p104r072","p104r073"]
    
    #create a big list of lines        
    lineList = [line.strip() for line in f]
    
    #for each item in the list, check whether it is in downloadScenes
    #if it is, write it into the output file
    for l in lineList:
        scene = "p%sr%s"%(l[3:6],l[6:9])
        if scene in downloadScenes:
            g.write(l + "\n")
    f.close()
    g.close()


# Command arguments
class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()
        p.add_option("-s", "--sceneList", dest= "sceneList", default=None,
            help = "file of all missing scene ids for NT output from usgs_list_missing.py")
        p.add_option("-o", "--outFile", dest= "outFile", default=None,
            help = "output text file of subset scene id's yet to be downloaded for pilot areas")    
        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)


if __name__ == "__main__":
    cmdargs = CmdArgs()
    mainRoutine(cmdargs)
