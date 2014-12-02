#!/usr/bin/env python
"""
Created on Tue Nov 12 13:56:08 2013

@author: barnetj

interactive scatter plot. plots x and y and then on mouse click returns the chosen vale and the x and y coordinate
"""

# get all the imports

#from __future__ import print_function
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.image import AxesImage
import numpy as np
from numpy.random import rand
import argparse
import csv
import os

def getCmdargs():
    p = argparse.ArgumentParser()
    
    p.add_argument("--inputTable", help="name of input csv table containing x,y and unique identifier")
    
    cmdargs = p.parse_args()
    
    if cmdargs.inputTable is None:
        p.print_help()
        sys.exit()
    return cmdargs
    

    
    
def mainRoutine():
    
    cmdargs = getCmdargs()
    
    
    #data input
    x = []
    y = []
    siteID = []
    infile = open(cmdargs.inputTable, "rb")
    reader = csv.reader(infile)
    
    for row in reader:
        
        x.append(float(row[0]))
        
        y.append(float(row[1]))

        siteID.append(row[2])
         
    
    fig, ax = plt.subplots()
    
    col = ax.scatter(x, y, picker=True)
    
    #fig.savefig('pscoll.eps')
    
    fig.canvas.mpl_connect('pick_event', onpick)

    plt.show()

    
def onpick(event):
    
    ind = event.ind
    
    print('onpick scatter:', ind)
    
    
    
if __name__ == "__main__":
    mainRoutine() 




