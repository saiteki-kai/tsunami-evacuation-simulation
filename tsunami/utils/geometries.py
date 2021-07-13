import haversine as hs
import osmnx as ox


def save(gdf, path):
    gdf = gdf.apply(lambda c: c.astype(str) if c.name != "geometry" else c, axis=0)
    gdf.to_file(path, driver="GPKG")


def load(path):
    ox.geometries_from_xml(path)


def find_nearest_nodes(graph, point, thresh=500, thresh_inc=50):
    nodes = []

    for n in graph.nodes:
        node = graph.nodes[n]
        if "lat" in node and "lon" in node:
            node_point = (node["lon"], node["lat"])

            if hs.haversine(node_point, point, unit=hs.Unit.METERS) < thresh:
                nodes.append(n)

    if len(nodes) > 1:
        return nodes

    return find_nearest_nodes(graph, point, thresh=thresh + thresh_inc, thresh_inc=thresh_inc)
