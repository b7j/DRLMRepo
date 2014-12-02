"""
Given a polygon layer, with paddocks/landtypes, we want to summarise
the cover over time for each pixel.

## first get an image about the correct extent
## lets work in EPSG:3577
ogr2ogr -t_srs EPSG:3577 -f "ESRI Shapefile" strata2.shp strat.shp
ogrinfo strata2.shp strata2 -so|grep Extent

## these are all available, so
## from athena we can do
#Extent: (347693.130307, -2059917.829890) - (470087.659728, -1934973.572621)


projwin="347693.130307 -1934973.572621 470087.659728 -2059917.829890"

for img in $(find /apollo/imagery/rsc/landsat/mosaics/nt -name "*dima2.tif")
do
outimg=$(basename $img)
outimg=${outimg/nt/brunettte_downs}
outimg=${outimg/.tif/.img}
gdal_translate -of HFA \
   -projwin $projwin \
   $img \
   $outimg
done

## and create an output image
gdal_translate -b 1 lztmre_brunettte_downs_m199709199711_dima2.img strata2.tif
gdal_rasterize -i -burn 0 -l strata2 strata2.shp strata2.tif
gdal_rasterize -burn 1 -l strata2 strata2.shp strata2.tif #Calcarosols by default
gdal_rasterize -burn 2 -where 'SOIL="Kandosols"' -l strata2 strata2.shp strata2.tif
gdal_rasterize -burn 3 -where 'SOIL="Rudosols"' -l strata2 strata2.shp strata2.tif
gdal_rasterize -burn 4 -where 'SOIL="Vertosols"' -l strata2 strata2.shp strata2.tif
## strat.shp has paddock by soil boundaries
## we've only got Vertosols and Calcarosols
## gdal_rasterize -burn 1 -where 'SOIL="Vertosols"' -l strat strat.shp strat.tif

## now we can open each and summarise by percentile

## run the script, then run the summarise percentiles one,
## then you can summarise by polygon
## I added a field stratid=$rownum
qv_rastbypoly.py -r lztmre_brunettte_downs_y19872013_psuma2.img -v strata2.shp -o strata2summary.csv -c stratid --doheadings

## which you can then join
"""

from osgeo import gdal
import numpy as np
import sys

## we read the whole image in,
## so we don't bother with rios

inimage = sys.argv[1]
print inimage
maskimage = "strata2.tif"
outimage = inimage.replace('dima2','percenta2')
driver = gdal.GetDriverByName("HFA")

dimDS = gdal.Open(inimage)
maskDS = gdal.Open(maskimage)

percentDS = driver.CreateCopy( outimage, maskDS, 0 )

## get the data
## we want green + dry = 100 - bare
## bare is the first
bareBand = dimDS.GetRasterBand(1)
bare = bareBand.ReadAsArray() ## pretty big!

mask = maskDS.ReadAsArray()


maskvals = list(set(mask.flatten()))
outdata = np.zeros_like(mask) + 200
for thissoil in maskvals[1:]:
    ## get percentiles
    thisdata = 200 - bare[(bare > 99) & (bare < 201) & (mask==thissoil)]
    if thisdata.size > 0:
        pct = np.percentile(thisdata, list(np.arange(100)))
        pctatpoint = np.interp(thisdata, pct, np.arange(100))
        outdata[(bare > 99) & (bare < 201) & (mask==thissoil)] = pctatpoint.astype('uint8')


band = percentDS.GetRasterBand(1)
band.WriteArray(outdata)

band = None
percentDS = None
dimDS = None
maskDS = None



