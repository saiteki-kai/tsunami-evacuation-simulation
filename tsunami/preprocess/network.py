import os
import sys

import osmnx as ox

from tsunami.config import POINT, DIST, CRS, DATA_DIR
from tsunami.utils import geometries

ox.config(use_cache=True, log_console=True)


def main():
    graph = ox.graph_from_point(POINT, dist=DIST, network_type="all")

    G = ox.project_graph(graph, to_crs=CRS)
    G = ox.consolidate_intersections(G, tolerance=10, rebuild_graph=True, dead_ends=True)
    ox.save_graphml(G, os.path.join(DATA_DIR, "graph.xml"))

    buildings = ox.geometries_from_point(POINT, {"building": True}, dist=DIST)
    geometries.save(buildings, os.path.join(DATA_DIR, "buildings.gpkg"))

    coastline = ox.geometries_from_point(POINT, {"place": "island"}, dist=DIST)
    geometries.save(coastline, os.path.join(DATA_DIR, "coastline.gpkg"))


if __name__ == "__main__":
    sys.exit(main())
