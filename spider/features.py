import json
from pathlib import Path

from scipy import ndimage
import geopandas as gpd
import h3pandas  # noqa: W

import rasterio
from rasterio.features import rasterize
from rasterstats import zonal_stats


def create_hex(aoi: gpd.GeoDataFrame, resolution=5):
    return aoi.h3.polyfill_resample(resolution).get(["geometry"])


def add_raster_layer(
    geom, raster, operation, col_name, affine=None, crs=None, decimals=2
):
    """
    Add a raster layer

    Parameters
    ----------
    geom: geopandas.GeoDataFrame
        The processed geom.
    raster: str, pathlib.Path or numpy.ndarray
        Either a path to the raster, or numpy.ndarray with the data.
    operation: str
        The operation to perform when extracting the raster data.
        Either 'sum', 'max', or 'mean'
    col_name: str
        Name of the column to add.
    affine: affine.Affine(), optional
        If a numpy ndarray is passed above, the affine is also needed.
    crs: proj.crs, optional
        Override raster's reported crs

    Returns
    -------
    geom: geopandas.GeoDataFrame
        The processed geom with new column.
    """

    if isinstance(raster, Path):
        raster = str(raster)
    if isinstance(raster, str):
        # rasterstats doesn't check for same CRS
        # Throws memory error if don't ensure they are same
        if not crs:
            crs = rasterio.open(raster).crs
        geom_proj = geom.to_crs(crs)
        stats = zonal_stats(geom_proj, raster, stats=operation)

        geom_proj[col_name] = [x[operation] for x in stats]

        geom = geom_proj.to_crs(geom.crs)
        geom[col_name] = geom[col_name].fillna(0)
        geom[col_name] = geom[col_name].round(decimals)

        return geom

    else:
        raise NotImplementedError("Only implemented for path input.")


def add_vector_layer(geom, vector, operation, col_name, raster_like, decimals=2):
    """
    Use a vector containing grid infrastructure to determine
    each cluster's distance from the grid.

    Parameters
    ----------
    geom: geopandas.GeoDataFrame
        The processed geom.
    vector: str, pathlib.Path or geopandas.GeoDataFrame
        Path to or already imported grid dataframe.
    operation: str
        Operation to perform in extracting vector data.
        Currently only 'distance' supported.
    raster_like: file-like
        Raster file to use for crs, shape, affine when rasterizing vector

    Returns
    -------
    geom: geopandas.GeoDataFrame
        The processed geom with new column.
    """

    if isinstance(vector, Path):
        vector = str(vector)
    if isinstance(vector, str):
        vector = gpd.read_file(vector)

    with rasterio.open(raster_like) as rd:
        crs = rd.crs
        affine = rd.transform
        shape = rd.shape

    vector = vector.to_crs(crs=crs)
    geom = geom.to_crs(crs=crs)

    if operation == "distance":
        vector = vector.loc[vector["geometry"].length > 0]

        grid_raster = rasterize(
            vector.geometry,
            out_shape=shape,
            fill=1,
            default_value=0,
            all_touched=True,
            transform=affine,
        )
        dist_raster = ndimage.distance_transform_edt(grid_raster) * affine[0]

        dists = zonal_stats(
            vectors=geom, raster=dist_raster, affine=affine, stats="min"
        )
        geom[col_name] = [x["min"] for x in dists]
        geom[col_name] = geom[col_name].fillna(0)
        geom[col_name] = geom[col_name].round(decimals)
        geom = geom.to_crs(epsg=4326)

        return geom

    else:
        raise NotImplementedError('Currently only "distance" is supported.')


def fix_column(
    geom,
    col_name,
    factor=1,
    minimum=0,
    maximum=None,
    no_value=None,
    per_capita=False,
):
    """
    A number of operations to apply to a columns values to get desired output.

    Parameters
    ----------
    geom : GeoDataFrame
        The geom object.
    col_name : str
        The column to apply the operation to.
    factor : float, optional (default 1.)
        Factor by which to multiply the column vales.
    minimum : float, optional (default 0.)
        Apply a minimum threshold to the values.
    maximum : str, optional
        Currently only supported for 'largest'.
        Limits the values to double the value of the cluster with the highest
        population.
    no_value : str, optional
        Currently only supported for 'median'.
        Replaces NaN instances with the median value.
    per_capita : boolean, optional (default False.)
        Divide values by cluster population.

    Returns
    -------
    geom : GeoDataFrame
        The 'fixed' geom.
    """

    # multiply the column by a fixed factor
    if factor is not None and factor != 1:
        geom[col_name] = geom[col_name] * factor

    # remove negative values
    if minimum is not None:
        geom.loc[geom[col_name] < minimum, col_name] = minimum

    if per_capita:
        geom[col_name] = geom[col_name] / geom["pop"]

    # apply a cutoff maximum value
    if maximum is not None:
        if maximum == "largest":
            limit = 2 * float(
                geom.loc[geom["pop"] == geom["pop"].max(), col_name].tolist()[0]
            )
            geom.loc[geom[col_name] > limit, col_name] = limit

        else:
            raise NotImplementedError("maximum only implemented for largest.")

    # replace nan values
    if no_value is not None:
        if no_value == "median":
            replace = {col_name: geom[col_name].median()}
            geom = geom.fillna(value=replace)

        else:
            raise NotImplementedError("no_value only implemented for median.")

    return geom


def save_geom(geom, out_path):
    """
    Convert to EPSG:4326 and save to the specified file.
    geom: geopandas.GeoDataFrame
        The processed geom.
    out_path: str or pathlib.Path
        Where to save the geom file.
    """

    if isinstance(out_path, Path):
        out_path = str(out_path)
    if ".gpkg" in out_path:
        driver = "GPKG"
    elif ".geojson" in out_path or ".json" in out_path:
        driver = "GeoJSON"
    else:
        driver = None

    geom = geom.to_crs(epsg=4326)
    geom.to_file(out_path, driver=driver)
