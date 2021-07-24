import os

import contextily as ctx
import matplotlib.pyplot as plt
import osmnx as ox
from descartes import PolygonPatch
from shapely.geometry import MultiPolygon

from tsunami.config import DATA_DIR, OUTPUT_DIR
from tsunami.utils.geometries import load


class ModelViewer:
    def __init__(self, model):
        self.model = model

    def plot_agents(self):
        fig, ax = ox.plot_graph(self.model.G,
                                node_size=0,
                                edge_linewidth=1,
                                bgcolor="#0b3496",
                                figsize=(9, 9),
                                show=False)

        positions = [a.pos for a in self.model.agents if a.pos is not None]
        x = [p[0] for p in positions]
        y = [p[1] for p in positions]
        ax.scatter(x, y, c="g", alpha=0.8, edgecolors='none')

        fig.tight_layout(pad=0.0)
        fig.show()

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
        path = os.path.join(DATA_DIR, "safe_area.gpkg")
        boundary = load(path)
        self.__add_polygon(boundary, ax, fc="w", lw=2, alpha=0.5, zorder=-1)

        fig.tight_layout(pad=0.0)

        if show:
            fig.show()

        return fig, ax

    def plot_population(self, save=False):
        # fig, ax = self.model.agents.plot()
        gdf_nodes = ox.graph_to_gdfs(self.model.G, edges=False,
                                     fill_edge_geometry=False)

        ax = gdf_nodes.plot(marker=".", markersize=20, color="w", alpha=0.8, figsize=(10, 10))

        nc = []
        for n in self.model.G.nodes:
            print(n)
            print(len(self.model.G.nodes[n]["agents"]))
            n_agents = len(self.model.G.nodes[n]["agents"])
            if n_agents > 0:
                nc.append("yellow")
            else:
                nc.append("white")

        ax = gdf_nodes.plot(marker=".", markersize=20, color=nc, alpha=0.8, figsize=(10, 10))

        # load boundary polygon
        path = os.path.join(DATA_DIR, "districts.gpkg")
        boundary = load(path)
        cmap = plt.cm.get_cmap("hsv", len(boundary))
        self.__add_polygon(boundary, ax, cmap=cmap, lw=0, alpha=0.5, zorder=-1)
        self.__add_polygon(boundary, ax, fc="None", lw=2, alpha=1, zorder=1)

        ctx.add_basemap(ax, zoom=13, source=ctx.providers.Esri.WorldImagery, reset_extent=False,
                        zorder=-2)

        ax.margins(0)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.set(frame_on=False)

        w, s, e, n = gdf_nodes.total_bounds
        ax.set_xlim(w, e)
        ax.set_ylim(s, n)

        ax.set_axis_off()

        fig = plt.gcf()
        fig.tight_layout()
        # fig.show()

        if save:
            filepath = os.path.join(OUTPUT_DIR, "population.png")
            plt.savefig(filepath, transparent=True)

    def plot_route(self, route, show=True, save=False):
        fig, ax = ox.plot_graph_route(self.model.G, route,
                                      orig_dest_size=50,
                                      route_linewidth=2,
                                      node_size=0)

        # load boundary polygon
        path = os.path.join(DATA_DIR, "safe_area.gpkg")
        safe_area = load(path)
        self.__add_polygon(safe_area, ax, fc="g", lw=2, ls="--", alpha=0.5, zorder=1)

        fig.tight_layout()

        if save:
            filepath = os.path.join(OUTPUT_DIR, "route_a0.png")
            fig.savefig(filepath, transparent=True)

        if show:
            fig.show()

        return fig, ax

    @staticmethod
    def __add_polygon(gdf, ax, cmap=None, **kwargs):
        geometries = gdf['geometry']
        for i, geometry in enumerate(geometries):
            if cmap is not None:
                kwargs["fc"] = cmap(i)

            if not isinstance(geometry, MultiPolygon):
                geometry = MultiPolygon([geometry])

            for polygon in geometry:
                patch = PolygonPatch(polygon, **kwargs)
                ax.add_patch(patch)
