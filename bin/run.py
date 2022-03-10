#!/usr/bin/env python3

import os
from pathlib import Path
import sys
import warnings

from typer import Typer, echo, Option
import yaml
import geopandas as gpd

from spider.features import add_raster_layer, add_vector_layer, fix_column, create_hex
from spider.model import Assumptions, Town, run_model

app = Typer()

cfg_default = Path(__file__).parents[1] / "config.yml"
warnings.simplefilter("ignore")


@app.command()
def feat(
    file: Path,
    config: Path = Option(cfg_default, help="Path to config file"),
    overwrite: bool = Option(False),
    js: bool = Option(False),
) -> None:
    """Add features."""

    file = Path(file)

    with config.open() as f:
        cfg = yaml.safe_load(f)

    if file.exists():
        geom = gpd.read_file(file)
    else:
        geom = gpd.read_file(cfg["aoi"])
        geom = create_hex(geom, cfg["hex_res"])

    for f in cfg["features"]:
        col_name = f["name"]
        if col_name not in geom.columns:
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
                    per_capita=fix["per_capita"]
                    if "per_capita" in fix.keys()
                    else None,
                )

    if not file.exists():
        geom = geom.reset_index()
    geom["fid"] = geom.index
    geom = geom.dropna(axis=0, subset=["geometry"])

    geom.geometry = geom.simplify(
        tolerance=0.001,
        preserve_topology=False,
    )
    if js:
        with open("dist/hex.js", "w") as f:
            print("export default", geom.to_json(), file=f)

    geom.to_file(file)


@app.command()
def model(
    in_file: Path,
    out_file: Path,
    sample: bool = Option(False),
):
    gdf = gpd.read_file(in_file)
    ass = Assumptions(mg_cost_pkw=2000)

    if sample:
        row = gdf.sample(1).iloc[0]
        town = Town.from_row(row)
        run_model(town, ass, verbose=True)

    else:
        data = [run_model(Town.from_row(row), ass) for idx, row in gdf.iterrows()]
        gdf["farm_type"] = [r.farm_type for r in data]
        gdf["fish_output"] = [r.fish_output for r in data]
        gdf["profit"] = [r.profit for r in data]
        gdf["gov_costs"] = [r.gov_costs for r in data]
        gdf["social"] = [r.social for r in data]
        print(f"Saving to {out_file}")
        breakpoint()
        gdf.to_file(out_file)


if __name__ == "__main__":
    app()
