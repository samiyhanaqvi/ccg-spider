import re
from pathlib import Path
import warnings

warnings.simplefilter("ignore")  # noqa

from typer import Typer, echo, Option  # noqa
import yaml  # noqa
import geopandas as gpd  # noqa

from spider.features import (  # noqa
    add_features,
    add_raster_layer,
    add_vector_layer,
    fix_column,
    create_hex,
)
from spider.neighbors import add_neighbors  # noqa

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
        echo("Loading and appending to existing file")
        geom = gpd.read_file(file)
    else:
        echo("Creating a new hex geometry from scratch")
        geom = gpd.read_file(cfg["aoi"])
        geom = create_hex(geom, cfg["hex_res"])
        geom = geom.reset_index(drop=True)
        geom = add_neighbors(geom)

    if "features" in cfg and isinstance(cfg["features"], list):
        echo("Adding features...")
        geom = add_features(geom, cfg["features"], cfg["raster_like"])
    else:
        echo("No features to add")

    geom["fid"] = geom.index
    geom["index"] = geom.index
    geom = geom.dropna(axis=0, subset=["geometry"])

    geom.geometry = geom.simplify(
        tolerance=0.001,
        preserve_topology=False,
    )
    echo(f"Saving to {file}")
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
