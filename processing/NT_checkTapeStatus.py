#!/usr/bin/env python

import qvf

filelist = [line.strip() for line in open('/scratch/rsc5/jason/validation/inputs/imagery/std/dc4/dc4missing.txt')]

filelist2 = ["/apollo/imagery/rsc/%s/%s" % (qvf.qvladmsubdir(fn), fn) for fn in filelist]

f = open('images_fullpath.txt', 'w')

for fn in filelist2:

    f.write(fn+'\n')
 
f.close()

