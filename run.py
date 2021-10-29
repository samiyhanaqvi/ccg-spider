#!/usr/bin/env python3

import os
from pathlib import Path
import warnings

from typer import Typer, echo, Option
import yaml
import geopandas as gpd

from spider.features import add_raster_layer, add_vector_layer, fix_column, create_hex

app = Typer()

script_dir = Path(os.path.dirname(__file__))
cfg_default = script_dir / "features.yml"


@app.command()
def feat(
    aoi_in: Path,
    geom_out: Path,
    config: Path = Option(cfg_default, help="Path to config file"),
):
    """Add features."""

    with config.open() as f:
        cfg = yaml.safe_load(f)

    geom = gpd.read_file(aoi_in)
    geom = create_hex(geom, 3)

    for f in cfg:
        echo(f["name"])
        if f["type"] == "raster":
            geom = add_raster_layer(
                geom=geom,
                raster=Path(f["file"]).expanduser(),
                operation=f["operation"],
                col_name=f["name"],
                crs=f["crs"] if "crs" in f.keys() else None,
                decimals=f["decimals"],
            )

        elif f["type"] == "vector":
            geom = add_vector_layer(
                geom=geom,
                vector=Path(f["file"]).expanduser(),
                operation=f["operation"],
                col_name=f["name"],
                raster_like=f["raster_like"],
                decimals=f["decimals"],
            )

        else:
            raise ValueError("Only 'raster' or 'vector' supported for 'type'.")

        if "fix" in f:
            geom = fix_column(
                geom=geom,
                col_name=f["name"],
                factor=f["factor"] if "factor" in f.keys() else None,
                minimum=f["minimum"] if "minimum" in f.keys() else None,
                maximum=f["maximum"] if "maximum" in f.keys() else None,
                no_value=f["no_value"] if "no_value" in f.keys() else None,
                per_capita=f["per_capita"] if "per_capita" in f.keys() else None,
            )

    # geom = geom.to_crs(epsg=102022)
    geom["area"] = geom.geometry.area
    geom["x"] = geom.geometry.centroid.x
    geom["y"] = geom.geometry.centroid.y
    # geom = geom.to_crs(epsg=4326)

    geom = geom.sort_values(by="area", ascending=False)
    geom["fid"] = geom.index
    geom = geom.dropna(axis=0, subset=["geometry"])
    geom = geom.fillna(0)  # There were NaN in NTL (at least)
    geom = geom.loc[geom["area"] > 0]

    geom.geometry = geom.simplify(
        tolerance=0.001,
        preserve_topology=False,
    )
    geom.to_file(geom_out, driver="GeoJSON")


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    app()
