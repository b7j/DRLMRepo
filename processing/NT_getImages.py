#!/usr/bin/env python
"""
Work out all the file names for the given path/row and stage. 
Recall them to the current directory. 

"""
import argparse
import sys
import pdb
import os

import qv
from rsc.utils import metadb

def getCmdargs():
    p = argparse.ArgumentParser()
    p.add_argument("--path", type=int, help="path, ie 102")
    p.add_argument("--row", type=int, help="row, ie 77")
    p.add_argument("--stage", help = "processing stage, ie dil")
    p.add_argument("--destDir", help = "destination directory")
    
    cmdargs = p.parse_args()
    if cmdargs.path is None:
        p.print_help()
        sys.exit()

    return cmdargs


def getImageNames(cmdargs):
    """
    Use the database to generate a list of all the filenames for the given scene, 
    for the given stage. 
    """
    scene = "p%3.3dr%3.3d" % (cmdargs.path, cmdargs.row)
    sql = """
        select satellite, instrument, date 
        from landsat_list 
        where product = 're' and scene = '%s'
        order by date
    """ % scene
    
    DBcon = metadb.connect(api=metadb.DB_API)
    DBcursor = DBcon.cursor()
    DBcursor.execute(sql)
    results = DBcursor.fetchall()
    #pdb.set_trace()
    fileList = []
    for (sat, instr, date) in results:
	
	newDate = date[0:4]
        filename = "lztmre_%s_%s_%sm3.img" % (scene, newDate, cmdargs.stage)
        # Use the database to get the right projection code for this scene
        filename = metadb.stdProjFilename(filename, cursor=DBcursor)
        fileList.append(filename)
    
    return fileList
    
    #pdb.set_trace()

def main():
    """
    Main routine
    """
    cmdargs = getCmdargs()

    #pdb.set_trace()

    fileNameList = getImageNames(cmdargs)
    
    a= set(fileNameList)
    
    fileNameList = list(a)
        
    for f in fileNameList:
	    
	    cmd = "qv_recall_to_pc --destdir %s %s" % (cmdargs.destDir, f) # call the standard mask
        
            os.system(cmd) 


if __name__ == "__main__":
    main()
