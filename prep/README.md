# spider-prep

# Data preparation
## AOI
Download eg [GADM](https://gadm.org/download_country_v3.html) and export only level-0 as `GeoPackage`.

## HRSL
Download from [HDX](https://data.humdata.org/dataset/highresolutionpopulationdensitymaps-ken).
```bash
gdal_translate -co COMPRESS=LZW ken_2020.tif hrsl_comp.tif
```

## Blank template raster
To use in generating rasters from vectors:
```bash
gdalwarp -tr 0.005 0.005 hrsl.tif blank.tif
gdalwarp -t_srs EPSG:4088 blank.tif blank_proj.tif
```


## GRID3 settlements
From [CIESEN](https://academiccommons.columbia.edu/doi/10.7916/d8-3tn0-1686).

Convert to `GeoPackage` in QGIS.

## Urban towns
Zonal stats HRSL into GRID3 `bua` settlements. Filter for `pop_sum > 10000`.

## Distance from urban towns to big cities
NB: Not used currently.

Manually draw Nairobi and Mombasa. Use `dist_city.py` to get distances.

## OSM
### Download
Download `.osm.pbf` from [Geofabrik](https://download.geofabrik.de/africa.html).

### Convert
```bash
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
```bash
export GDAL_CONFIG_FILE=/usr/share/gdal/osmconf.ini
osmfilter kenya.o5m --keep="power=line" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select power,voltage -f GPKG grid.gpkg /vsistdin/ lines
osmfilter kenya.o5m --keep="highway=motorway =trunk =primary =secondary =tertiary" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select highway -f GPKG roads.gpkg /vsistdin/ lines
osmfilter kenya.o5m --keep="water=lake =river =oxbow =lagoon =reservoir" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select water -f GPKG lakes.gpkg /vsistdin/ multipolygons
osmfilter kenya.o5m --keep="water=lake =river =oxbow =lagoon =reservoir" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select water -f GPKG rivers.gpkg /vsistdin/ lines
osmfilter kenya.o5m --keep="natural=wood landuse=forest" | ogr2ogr -oo CONFIG_FILE=$GDAL_CONFIG_FILE -select natural,landuse -f GPKG forest.gpkg /vsistdin/ multipolygons
```

Lake Victoria is manually extracted to `victoria.gpkg`.

## Precipitation
Using [WorldClim data](https://www.worldclim.org/data/worldclim21.html) for precipitation at 30s spatial resolution.

Merge the monthly rasters with gdal:
```bash
gdal_calc.py -A *.tif --calc="numpy.sum(A, axis=0)" --outfile=precip_mean.tif
```

# Extracting features
Install this package:
```bash
git clone https://github.com/carderne/ccg-spider.git
cd ccg-spider/prep
pip install -e .
```

Edit feature definitions in `config.yml` and then:
```bash
spi feat processed/hex.gpkg
spi nei processed/hex.gpkg processed/nei.gpkg
spi js processed/nei.gpkg ../frontend/dist/hex.js
```
