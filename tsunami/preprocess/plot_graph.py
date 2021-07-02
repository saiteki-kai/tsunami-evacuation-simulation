import sys
import osmnx as ox

from tsunami.config import *

ox.config(use_cache=True, log_console=True)


def main():
    G = ox.load_graphml(os.path.join(DATA_DIR, "graph.xml"))

    ___, ax = ox.plot_graph(G, show=True, node_size=0)
    # ___, ax = ox.plot_footprints(coastline, ax, show=False, color="white", alpha=0.2, bgcolor="lightblue")
    # fig, __ = ox.plot_footprints(buildings, ax, show=True, color="orange", bgcolor="lightblue")

    # fig.tight_layout()
    # fig.savefig("images/graph.png", dpi=600, transparent=True)


if __name__ == "__main__":
    sys.exit(main())
