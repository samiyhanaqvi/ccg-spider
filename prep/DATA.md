# spider-data
This is a list of common data sources that you might want to integrate with the model

## HRSL
Download from [HDX](https://data.humdata.org/dataset/highresolutionpopulationdensitymaps-ken).
(This example is for Kenya, but many countries are available by searching on HDX.

You can use this command to decrease the file size (if needed).
```bash
gdal_translate -co COMPRESS=LZW hrsl.tif hrsl_comp.tif
```

## GRID3 settlements
From [CIESEN](https://academiccommons.columbia.edu/doi/10.7916/d8-3tn0-1686).

Convert to `GeoPackage` in QGIS before saving to `data/`.

## Urban towns
To get a list of larger towns, the following procedure was used:
1. Use QGIS Zonal Stats to get HRSL population data into GRID3 `bua` settlements.
2. Filter for `pop_sum > 10000`.
3. Export to `data/`.

## OSM
### Download
Download the appropriate country-level `.osm.pbf` from [Geofabrik](https://download.geofabrik.de/africa.html).

### Convert
Convert to `o5m` to make it easier to work with.
```bash
osmconvert kenya.osm.pbf -o=kenya.o5m
```

### Extract
First edit `/usr/share/gdal/osmconf.ini` (this could be a different location on your installation) and add things of interest:
```ini
[lines]
...
attributes=...,power,voltage
```

Then set the environment variable path to this file:
```bash
export GDAL_CONFIG_FILE=/usr/share/gdal/osmconf.ini
```

This is a list of possible OSM extractions you could run.
If any don't work, you might need to add `-oo CONFIG_FILE=$GDAL_CONFIG_FILE` after `ogr2ogr`.
```bash
osmfilter kenya.o5m --keep="power=line" | \
  ogr2ogr -select power,voltage grid.gpkg /vsistdin/ lines

osmfilter kenya.o5m --keep="highway=motorway =trunk =primary =secondary =tertiary" | \
  ogr2ogr -select highway roads.gpkg /vsistdin/ lines

osmfilter kenya.o5m --keep="water=lake =river =oxbow =lagoon =reservoir" | \
  ogr2ogr -select water lakes.gpkg /vsistdin/ multipolygons

osmfilter kenya.o5m --keep="water=lake =river =oxbow =lagoon =reservoir" | \
  ogr2ogr -select water rivers.gpkg /vsistdin/ lines

osmfilter kenya.o5m --keep="natural=wood landuse=forest" | \
  ogr2ogr -select natural,landuse forest.gpkg /vsistdin/ multipolygons
```

## Precipitation
Using [WorldClim data](https://www.worldclim.org/data/worldclim21.html) for precipitation at 30s spatial resolution.

Merge the monthly rasters with GDAL to get an annual total:
```bash
gdal_calc.py -A *.tif --calc="numpy.sum(A, axis=0)" --outfile=precip_annual.tif
```
