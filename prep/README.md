# spider-prep
Please follow all the instructions below to create a hexagon data file that can be used by the spider app.

Key steps are noted with a 👉.

First clone this repository:
```bash
git clone https://github.com/carderne/ccg-spider.git
cd ccg-spider/prep
```

## Data preparation
The instructions below are for the two most important layers.
Please read [DATA.md](DATA.md) for some instructions for downloading additional layers
(such as population, settlements, OSM data).

To keep things organised, use the following data directories:
- [raw/](raw/): for raw data downloaded from the internet.
- [data/](data/): for the processed data that is ready to be ingest by the script.
- [processed/](processed/): for the output hexagon files.

### AOI
The only compulsory input layer is an AOI (area of interest) delineating the area to be modelled. Choose whether you want an administrative boundary or just to draw a custom AOI.

👉 Whichever one you use (administrative or custom) save the resulting file in the data directory as eg `data/aoi.gpkg` (or `data/aoi.geojson`).

### Country/administrative boundaries
Download [a GADM extract](https://gadm.org/download_country_v3.html) and export only level-0 as `GeoPackage`.
You can also export a different level if you want, for example, a specific administrative region within a country.

#### Custom AOI
You can also just go to [geojson.io](http://geojson.io/) and draw a polygon covering the area and download it as a GeoJSON.

### Blank raster
If you plan to calculate any distance layers (eg distance from hexagon to grid lines) you'll need a blank raster to use as a template.
You can create this as follows (replace `data/aoi.gpkg` with whatever you named the AOI fro above).
```bash
gdal_rasterize data/aoi.gpkg -burn 1 -tr 0.1 0.1 data/blank.tif
gdalwarp -t_srs EPSG:4088 blank.tif data/blank_proj.tif
```

## Installation
👉 Make sure you're in the `ccg-spider/prep` directory and install it
```bash
pip install -e .
```

## Configuration
👉 You must make a file called `config.yml` (inside the `prep` folder)
with at least the following contents:
```yaml
aoi: data/aoi.gpkg                  # path to the AOI you downloaded
hex_res: 3                          # see note below!
raster_like: data/blank_proj.tif    # path to the template raster you created
```

Have a look [here](https://h3geo.org/docs/core-library/restable)
to see details on the resolutions available.
A good choice for a medium sized country is `5`, or `4` for a very big one.
If you're doing a small area around a town, `8` might be more useful.
I recommend to start with `3`, check that everything works, and then go to higher resolutions.
(It will be much faster this way!)

## Hexagon time
👉 Once that is all done, you can run the script. Note that the output _must_ be a GeoJSON or it will complain.
```bash
spi processed/hex.geojson
```

And then you can move this GeoJSON to the appropriate location at `frontend/dist/models/model-name/hex.geojson`.

You can also point the script to a different config file:
```bash
spi --config=other_config.yml processed/other_hex.geojson
```

If you run `spi` and provide a path to a file that _already exists_, it will overwrite that file. If you want, you can run the script as below, and then only new columns from `config.yml` will be added (this might be risky).
```bash
spi processed/hex.geojson --append
```

## Additional layers
I'd recommend to try it just like that to make sure everything works.
But once you've successfully run the scripts (see above), you need to add some more layers.
So follow these instructions, and then run the `spi` script again.

Have a look at [config_example.yml](config_example.yml) to see a full example of how you can add layers. Basically, it looks like this:
```yaml
# ignoring the aoi, hex_res stuff at the top

features:  # this must only appear once!
           # just add more blocks like the below

  - name:       # name the column will get
    type:       # column or vector
    file:       # source file containing the data to be extracted
    operation:  # either sum/mean (raster) or distance/sjoin (vector)
    decimals:   # number of decimal places to keep
    joined_col: # this is ONLY used for sjoin!
    fix:        # this and below are all optional
      minimum:  # minimum value to apply
      factor:   # constant to multipl by (eg m -> km)

```

### Raster layers
These are the simplest, and use zonal statistics to get data from a raster
into your hexagons.

Example with `sum`:
```yaml
  - name: pop
    type: raster
    file: data/hrsl.tif
    operation: sum
    decimals: 0
```

Example with `mean`:
```yaml
  - name: precip
    type: raster
    file: data/precip.tif
    operation: mean
    decimals: 0
    fix:
      minimum: 0
```

### Vector layers
There are currently two ways to use vector layers.

You can calculate every hexagons `distance` to some features:
```yaml
  - name: grid_dist
    type: vector
    operation: distance
    file: data/grid.gpkg
    decimals: 2
    fix:
      factor: 0.001
```

Or you can do a spatial join to extract information from overlapping features.
This example gets the name of the province that each hexagon is within.
```yaml
  - name: adm1
    type: vector
    operation: sjoin
    file: data/gadm1.gpkg
    joined_col: NAME_1  # this is the name of the column
                        # that you want from the vector file
```
