import re
from pathlib import Path
import warnings

warnings.simplefilter("ignore")  # noqa

from typer import Typer, echo, Option
import yaml
import geopandas as gpd

from spider.features import (
    add_raster_layer,
    add_vector_layer,
    fix_column,
    create_hex,
)
from spider.neighbors import add_neighbors

app = Typer()

cfg_default = Path(__file__).parents[1] / "config.yml"


@app.command()
def feat(
    file: Path,
    config: Path = Option(cfg_default, help="Path to config file"),
    append: bool = Option(False),
) -> None:
    """Add features."""

    file = Path(file)

    with config.open() as f:
        cfg = yaml.safe_load(f)

    if append and file.exists():
        geom = gpd.read_file(file)
    else:
        geom = gpd.read_file(cfg["aoi"])
        geom = create_hex(geom, cfg["hex_res"])
        geom = geom.reset_index(drop=True)
        geom = add_neighbors(geom)

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
                    joined_col=f.get("joined_col", None),
                )

            else:
                raise ValueError("Only 'raster' or 'vector' supported for 'type'.")

            if f.get("decimals"):
                geom[col_name] = geom[col_name].fillna(0).round(f["decimals"])

            if "fix" in f:
                fix = f["fix"]
                geom[col_name] = fix_column(
                    col=geom[col_name],
                    pop=geom.Pop if "Pop" in geom.columns else None,
                    factor=fix.get("factor"),
                    minimum=fix.get("minimum"),
                    no_value=fix.get("no_value"),
                    per_capita=fix.get("per_capita"),
                )

    geom["fid"] = geom.index
    geom["index"] = geom.index
    geom = geom.dropna(axis=0, subset=["geometry"])

    geom.geometry = geom.simplify(
        tolerance=0.001,
        preserve_topology=False,
    )
    geom.to_file(file)


@app.command()
def js(
    in_file: Path,
    out_file: Path,
):
    """Convert 'in_file' to JS at 'out_file'."""
    gdf = gpd.read_file(in_file)
    with open(out_file, "w") as f:
        gdf_json = gdf.to_json()
        gdf_json = re.sub(
            r'"id": "(\d*)"',
            lambda m: f'"id": {m.group(1)}',
            gdf_json,
        )
        print("export default", gdf_json, file=f)
