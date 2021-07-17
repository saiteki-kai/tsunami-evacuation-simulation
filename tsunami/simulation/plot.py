import os

import osmnx as ox
from descartes import PolygonPatch
from shapely.geometry import MultiPolygon

from tsunami.config import DATA_DIR
from tsunami.utils.geometries import load


class ModelViewer:
    def __init__(self, model):
        self.model = model

    def plot_street(self, show=True):
        # edge colors by travel time
        ec = [d["link"].t for u, v, d in self.model.G.edges(keys=False, data=True)]
        r = (max(ec) - min(ec))
        ec = [(x - min(ec)) / r if r > 0.0 else 0.0 for x in ec]
        ec = [(0.1, x, 0.1, 1.0) for x in ec]

        fig, ax = ox.plot_graph(self.model.G,
                                node_size=0,
                                edge_linewidth=1,
                                edge_color=ec,
                                bgcolor="#0b3496",
                                figsize=(9, 9),
                                show=False)

        # load boundary polygon
        path = os.path.join(DATA_DIR, "boundary.gpkg")
        boundary = load(path)
        geometry = boundary['geometry'][0]

        # add boundary polygon
        for polygon in MultiPolygon([geometry]):
            patch = PolygonPatch(polygon, fc='w', ec='w', ls="--", lw=2, alpha=0.4, zorder=-1)
            ax.add_patch(patch)

        fig.tight_layout(pad=0.0)

        if show:
            fig.show()

        return fig, ax


def plot_population(self):
    pass


def plot_route(self, route, show=True):
    fig, ax = ox.plot_graph_route(self.model.G, route,
                                  orig_dest_size=50,
                                  route_linewidth=2,
                                  node_size=0,
                                  bgcolor='k')

    fig.tight_layout(pad=0.0)

    if show:
        fig.show()

    return fig, ax
