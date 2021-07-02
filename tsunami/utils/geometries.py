import osmnx as ox


def save(gdf, path):
    gdf = gdf.apply(lambda c: c.astype(str) if c.name != "geometry" else c, axis=0)
    gdf.to_file(path, driver="GPKG")


def load(path):
    ox.geometries_from_xml(path)
