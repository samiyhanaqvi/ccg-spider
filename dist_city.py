import geopandas as gpd
from spider.features import add_vector_layer, fix_column


def main():
    geom = gpd.read_file("data/towns.gpkg")

    col_name = "city_dist"

    geom[col_name] = add_vector_layer(
        geom=geom,
        vector="data/cities.gpkg",
        operation="distance",
        raster_like="data/blank_proj.tif",
    )

    fix = {"factor": 0.001}
    geom[col_name] = fix_column(
        col=geom[col_name],
        pop=geom.Pop if "Pop" in geom.columns else None,
        factor=fix["factor"] if "factor" in fix.keys() else None,
        minimum=fix["minimum"] if "minimum" in fix.keys() else None,
        no_value=fix["no_value"] if "no_value" in fix.keys() else None,
        per_capita=fix["per_capita"] if "per_capita" in fix.keys() else None,
    )

    geom.to_file("data/towns_dists.gpkg")


if __name__ == "__main__":
    main()
