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
                                      node_size=0,
                                      show=False)

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

    def interactive_graph(self):
        fig, ax1 = ox.plot_graph(self.model.G, figsize=(12, 12), show=False, node_alpha=0.7,
                                 node_size=10)

        selected_points, = ax1.plot([], [], ms=5, color='r', marker='o', lw=0)
        selected_lines, = ax1.plot([], [], ms=0, color='r')
        info_text = ax1.annotate("", xy=(0.6, 0.05), xycoords='axes fraction', ha="left",
                                 backgroundcolor="w",
                                 bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 8})

        def onclick(event):
            if not event.dblclick:
                if event.button == 1:
                    point = (event.xdata, event.ydata)
                    nn, d = ox.nearest_nodes(self.model.G, point[0], point[1], return_dist=True)

                    if d > 150:
                        print("no nodes found")
                        return

                    node = self.model.G.nodes[nn]

                    info_text.set_text((
                        f"id: {nn}\n"
                        f"lat: {node['lat'] if 'lat' in node else '-'}\n"
                        f"lon: {node['lon'] if 'lon' in node else '-'}\n"
                        f"agents: {len(node['agents'])}\n"
                    ))

                    selected_points.set_data([node['x']], [node['y']])
                    selected_lines.set_data([], [])

                    fig.canvas.draw()
                    fig.canvas.flush_events()
                elif event.button == 3:
                    point = (event.xdata, event.ydata)
                    print("searching...")
                    ne, d = ox.nearest_edges(self.model.G, point[0], point[1],
                                             return_dist=True)

                    if d > 150:
                        print("no edges found")
                        return

                    edge = self.model.G.edges[ne]
                    x, y = edge['geometry'].xy
                    selected_points.set_data([x[0], x[len(x) - 1]], [y[0], y[len(x) - 1]])
                    selected_lines.set_data(x, y)

                    info_text.set_text((
                        "Edge Info\n"
                        f"id: {ne}\n"
                        f"highway: {edge['highway'] if 'highway' in edge else '-'}\n"
                        f"oneway: {edge['oneway'] if 'oneway' in edge else '-'}\n"
                        f"length: {str(round(edge['length'], 2)) + ' m' if 'length' in edge else '-'}\n"
                        f"min width: {edge['link'].w:.2f} m\n"
                        f"area: {edge['link'].a:.2f} m^2\n"
                        f"cost: {edge['cost']:.2f}\n\n"
                        "Queue Info\n"
                        f"velocity: {edge['link'].v:.2f} m/s\n"
                        f"storage capacity: {edge['link'].c} ped\n"
                        f"flow capacity: {edge['link'].q:.2f} ped/s\n"
                        f"travel time: {edge['link'].t:.2f} s\n"
                        f"queue used: {edge['link'].get_queue_used()}%"
                    ))

                    fig.canvas.draw()
                    fig.canvas.flush_events()

        cid = fig.canvas.mpl_connect("button_press_event", onclick)

        fig.tight_layout()
        plt.show()

        input("Press any key to close...")
        fig.canvas.mpl_disconnect(cid)

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
