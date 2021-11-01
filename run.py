#!/usr/bin/env python3

import os
import json
from pathlib import Path

from typer import Typer, echo, Option
import yaml
import geopandas as gpd

from spider.features import add_raster_layer, add_vector_layer, fix_column, create_hex

app = Typer()

cfg_default = Path(os.path.dirname(__file__)) / "config.yml"


@app.command()
def feat(
    config: Path = Option(cfg_default, help="Path to config file"),
):
    """Add features."""

    with config.open() as f:
        cfg = yaml.safe_load(f)

    geom = gpd.read_file(cfg["aoi"])
    geom = create_hex(geom, cfg["hex_res"])

    for f in cfg["features"]:
        col_name = f["name"]
        echo(col_name)
        if f["type"] == "raster":
            geom[col_name] = add_raster_layer(
                geom=geom,
                raster=Path(f["file"]).expanduser(),
                operation=f["operation"],
                crs=f["crs"] if "crs" in f.keys() else None,
            )

        elif f["type"] == "vector":
            geom[col_name] = add_vector_layer(
                geom=geom,
                vector=Path(f["file"]).expanduser(),
                operation=f["operation"],
                raster_like=cfg["raster_like"],
            )

        else:
            raise ValueError("Only 'raster' or 'vector' supported for 'type'.")

        geom[col_name] = geom[col_name].fillna(0).round(f["decimals"])

        if "fix" in f:
            fix = f["fix"]
            geom[col_name] = fix_column(
                col=geom[col_name],
                pop=geom.Pop if "Pop" in geom.columns else None,
                factor=fix["factor"] if "factor" in fix.keys() else None,
                minimum=fix["minimum"] if "minimum" in fix.keys() else None,
                no_value=fix["no_value"] if "no_value" in fix.keys() else None,
                per_capita=fix["per_capita"] if "per_capita" in fix.keys() else None,
            )

    geom["fid"] = geom.index
    geom = geom.dropna(axis=0, subset=["geometry"])

    geom.geometry = geom.simplify(
        tolerance=0.001,
        preserve_topology=False,
    )
    with open("dist/hex.js", "w") as f:
        print("export default", geom.to_json(), file=f)


if __name__ == "__main__":
    app()
