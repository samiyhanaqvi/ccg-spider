# CCG-Spider?

# Data preparation
## HRSL
Download from [HDX](https://data.humdata.org/dataset/highresolutionpopulationdensitymaps-ken).
```
gdal_translate -co COMPRESS=LZW ken_2020.tif hrsl_comp.tif
```

## GRID3 settlements
From [CIESEN](https://academiccommons.columbia.edu/doi/10.7916/d8-3tn0-1686).

Convert to `GeoPackage` in QGIS.

## OSM
### Download
Download `.osm.pbf` from [Geofabrik](https://download.geofabrik.de/africa.html).

### Convert
```
osmconvert kenya.osm.pbf -o=kenya.o5m
```

### Extract
(First edit `/usr/share/gdal/osmconf.ini` and add things of interest:
```
[lines]
...
attributes=...,power,voltage
```

Get desired features:
```
export GDAL_CONFIG_FILE=/usr/share/gdal/osmconf.ini
osmfilter kenya.o5m --keep="power=line" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select power,voltage -f GPKG grid.gpkg /vsistdin/ lines
osmfilter kenya.o5m --keep="highway=motorway =trunk =primary =secondary =tertiary" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select highway -f GPKG roads.gpkg /vsistdin/ lines
osmfilter kenya.o5m --keep="water=lake =river =oxbow =lagoon =reservoir" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select water -f GPKG lakes.gpkg /vsistdin/ multipolygons
osmfilter kenya.o5m --keep="water=lake =river =oxbow =lagoon =reservoir" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select water -f GPKG rivers.gpkg /vsistdin/ lines
osmfilter kenya.o5m --keep="natural=wood landuse=forest" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select natural,landuse -f GPKG forest.gpkg /vsistdin/ multipolygons
```
