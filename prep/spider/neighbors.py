import geopandas as gpd
import numpy as np
import pandas as pd


def add_neighbors(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Geom should already be a hex geometry."""
    orig_crs = gdf.crs
    gdf = gdf.to_crs(epsg=3857)

    nei = []
    for idx, row in gdf.iterrows():
        out = (
            gpd.GeoDataFrame(geometry=[row.geometry], crs=gdf.crs)
            .sjoin_nearest(gdf, how="left", max_distance=0.1)
            .index_right
        )
        out = out.loc[out != idx]
        out = np.pad(out, (0, 6 - len(out)))
        nei.append(out)

    nei = pd.DataFrame(nei, columns=[f"n{i}" for i in range(6)], index=gdf.index)

    gdf = pd.concat((gdf, nei), axis=1)
    gdf = gdf.to_crs(orig_crs)
    return gdf
