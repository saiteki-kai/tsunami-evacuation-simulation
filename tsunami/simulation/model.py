import os
import random
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox

from tsunami.simulation.agents.resident import Resident
from tsunami.simulation.link import Link, choice_link
from tsunami.utils.geometries import find_nearest_nodes
from tsunami.utils.roads import get_width


def _save_and_show(fig, ax, save=False, show=True, close=True, filepath=None, dpi=300):
    fig.canvas.draw()
    fig.canvas.flush_events()

    if save:
        # default filepath, if none provided
        filepath = Path(filepath)

        # if save folder does not already exist, create it
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # get the file extension and figure facecolor
        ext = filepath.suffix.strip(".")
        fc = fig.get_facecolor()

        if ext == "svg":
            # if the file format is svg, prep the fig/ax for saving
            ax.axis("off")
            ax.set_position([0, 0, 1, 1])
            ax.patch.set_alpha(0.0)
            fig.patch.set_alpha(0.0)
            fig.savefig(filepath, bbox_inches=0, format=ext, facecolor=fc, transparent=True)
        else:
            # constrain saved figure's extent to interior of the axis
            extent = ax.bbox.transformed(fig.dpi_scale_trans.inverted())

            # temporarily turn figure frame on to save with facecolor
            fig.set_frameon(True)
            fig.savefig(
                filepath, dpi=dpi, bbox_inches=extent, format=ext, facecolor=fc, transparent=True
            )
            fig.set_frameon(False)  # and turn it back off again

    if show:
        plt.show()

    if close:
        plt.close()

    return fig, ax


def _config_ax(ax, crs, bbox, padding):
    # set the axis view limits to bbox + relative padding
    north, south, east, west = bbox
    padding_ns = (north - south) * padding
    padding_ew = (east - west) * padding
    ax.set_ylim((south - padding_ns, north + padding_ns))
    ax.set_xlim((west - padding_ew, east + padding_ew))

    # set margins to zero, point ticks inward, turn off ax border and x/y axis
    # so there is no space around the plot
    ax.margins(0)
    ax.tick_params(which="both", direction="in")
    _ = [s.set_visible(False) for s in ax.spines.values()]
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # set aspect ratio
    if ox.projection.is_projected(crs):
        # if projected, make equal aspect ratio
        ax.set_aspect("equal")
    else:
        # if not projected, conform aspect ratio to not stretch plot
        cos_lat = np.cos((south + north) / 2 / 180 * np.pi)
        ax.set_aspect(1 / cos_lat)

    return ax


def plot_graph(
        G, ax=None, figsize=(8, 8), bgcolor="#111111",
        node_color="w", node_size=15, node_alpha=None, node_edgecolor="none", node_zorder=1,
        edge_color="#999999", edge_linewidth=1, edge_alpha=None,
        show=True, close=False, save=False, filepath=None, dpi=300,
        bbox=None, padding=0):
    """
    Plot a graph.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    ax : matplotlib axis
        if not None, plot on this preexisting axis
    figsize : tuple
        if ax is None, create new figure with size (width, height)
    bgcolor : string
        background color of plot
    node_color : string or list
        color(s) of the nodes
    node_size : int
        size of the nodes: if 0, then skip plotting the nodes
    node_alpha : float
        opacity of the nodes, note: if you passed RGBA values to node_color,
        set node_alpha=None to use the alpha channel in node_color
    node_edgecolor : string
        color of the nodes' markers' borders
    node_zorder : int
        zorder to plot nodes: edges are always 1, so set node_zorder=0 to plot
        nodes below edges
    edge_color : string or list
        color(s) of the edges' lines
    edge_linewidth : float
        width of the edges' lines: if 0, then skip plotting the edges
    edge_alpha : float
        opacity of the edges, note: if you passed RGBA values to edge_color,
        set edge_alpha=None to use the alpha channel in edge_color
    show : bool
        if True, call pyplot.show() to show the figure
    close : bool
        if True, call pyplot.close() to close the figure
    save : bool
        if True, save the figure to disk at filepath
    filepath : string
        if save is True, the path to the file. file format determined from
        extension. if None, use settings.imgs_folder/image.png
    dpi : int
        if save is True, the resolution of saved file
    bbox : tuple
        bounding box as (north, south, east, west). if None, will calculate
        from spatial extents of plotted geometries.

    Returns
    -------
    fig, ax : tuple
        matplotlib figure, axis
    """
    max_node_size = max(node_size) if hasattr(node_size, "__iter__") else node_size
    max_edge_lw = max(edge_linewidth) if hasattr(edge_linewidth, "__iter__") else edge_linewidth
    if max_node_size <= 0 and max_edge_lw <= 0:  # pragma: no cover
        raise ValueError("Either node_size or edge_linewidth must be > 0 to plot something.")

    # create fig, ax as needed
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, facecolor=bgcolor, frameon=False)
        ax.set_facecolor(bgcolor)
    else:
        fig = ax.figure

    if max_edge_lw > 0:
        # plot the edges' geometries
        gdf_edges = ox.utils_graph.graph_to_gdfs(G, nodes=False)["geometry"]
        ax = gdf_edges.plot(ax=ax, color=edge_color, lw=edge_linewidth, alpha=edge_alpha, zorder=1)

    if max_node_size > 0:
        # scatter plot the nodes' x/y coordinates
        gdf_nodes = ox.utils_graph.graph_to_gdfs(G, edges=False, node_geometry=False)[["x", "y"]]
        ax.scatter(
            x=gdf_nodes["x"],
            y=gdf_nodes["y"],
            s=node_size,
            c=node_color,
            alpha=node_alpha,
            edgecolor=node_edgecolor,
            zorder=node_zorder,
        )

    # get spatial extents from bbox parameter or the edges' geometries
    # padding = 0
    if bbox is None:
        try:
            west, south, east, north = gdf_edges.total_bounds
        except NameError:
            west, south = gdf_nodes.min()
            east, north = gdf_nodes.max()
        bbox = north, south, east, west
        # padding = 0.02  # pad 2% to not cut off peripheral nodes' circles

    # configure axis appearance, save/show figure as specified, and return
    ax = _config_ax(ax, G.graph["crs"], bbox, padding)
    fig, ax = _save_and_show(fig, ax, save, show, close, filepath, dpi)
    return fig, ax


class EvacuationModel:
    def __init__(self, graph, time_step, simulation_time=None):
        self.G = graph
        self.shelters = []

        self.agents = []
        self.total_agents = 0
        self.evacuated_agents = 0
        self.dead_agents = 0

        self.T = time_step
        self.ST = simulation_time
        self.k = 0

    def init_state(self, population, shelters, tsunami):
        self.__init_queues()
        self.__add_population(population)
        self.__add_shelters(shelters)
        self.__assign_destinations()
        self.__add_routes()
        self.__add_tsunami(tsunami)

    def reset_state(self):
        self.total_agents = 0
        self.evacuated_agents = 0
        self.dead_agents = 0

    def step(self):
        print(
            f"# time step {self.k} \t {round(self.k * self.T, 2):2d} / {self.ST} minutes -------------------"
        )

        for curr_node in self.G.nodes:
            # estrarre l'agente prima
            edge = choice_link(self.G, curr_node)

            if edge is not None:
                link = self.G.edges[edge]["link"]

                link.update_velocity()
                new_cost = link.update_travel_time()
                self.G.edges[edge]["cost"] = new_cost

                u, v, _ = edge
                print(
                    f"velocity: {link.v:.2f} m/s\t travel time: {link.t:.2f}s\t queue: [{u} -> {v}] {link.get_queue_used()}% {link.queue.qsize()}"
                )

        for curr_edge in self.G.edges:
            edge = self.G.edges[curr_edge]
            _, v, _ = curr_edge

            if "link" in edge:
                # dequeue
                agents = edge["link"].dequeue(self.k, self.T)

                # add agents to the next node (v)
                self.G.nodes[v]["agents"].extend(agents)

    def run_iteration(self):
        print("# ---------------------------------------------------")

        while not self.__finished():
            self.step()
            self.k += 1

        print("# ---------------------------------------------------")

    def __finished(self):
        if self.ST is not None:
            return self.k >= int(self.ST // self.T)

        return self.evacuated_agents + self.dead_agents != self.total_agents

    def __add_population(self, population):
        self.total_agents = population['population'].sum()

        nx.set_node_attributes(self.G, {n: [] for n in self.G.nodes}, "agents")
        print(population.head(4))
        for p in range(len(population)):
            name = population["name"][p]
            quantity = population["population"][p]
            polygon = population["geometry"][p]

            agents = [Resident(f"{name}#{i}") for i in range(quantity)]
            self.agents.extend(agents)

            gdf_nodes = ox.graph_to_gdfs(self.G, edges=False, fill_edge_geometry=False)
            nodes_indices = gdf_nodes[gdf_nodes.geometry.within(polygon)].index.values
            K = min(quantity, len(nodes_indices))

            print(f"nodes found: {K:3d}\t population: {quantity:4d}\t n_indices: {len(nodes_indices)}\t")

            partitions = np.array_split(agents, K)

            for k in range(K):
                idx = random.randint(0, len(nodes_indices) - 1) if len(nodes_indices) > quantity else k
                n = nodes_indices[idx]

                part = partitions[k].tolist()
                self.G.nodes[n]["agents"].extend(part)

    def __add_shelters(self, shelters):
        pass

    def __add_tsunami(self, tsunami):
        pass

    def __assign_destinations(self):
        pass
        #for n in self.agents:
        #    agent = self.agents[n]
            # agent.dest = self.__choice_shelter(agent.origin)

    def __choice_shelter(self, node):
        gdf = ox.graph_to_gdfs(self.G, edges=False)
        gdf.query()
        return None

    def __add_routes(self):
        pass
        # for n in self.agents:
        #    agent = self.agents[n]
        #    self.__compute_route(agent)

    def __init_queues(self):
        for e in self.G.edges:
            edge = self.G.edges[e]

            length = edge["length"]
            width = get_width(edge["highway"], edge["lanes"] if "lanes" in edge else 0)
            area = length * width

            link = Link(length, width, area)

            edge["link"] = link
            edge["cost"] = link.get_travel_time()

    def compute_route(self, agent):
        if agent.dest is None:
            raise ValueError("Agent destination not specified!")

        orig = agent.orig
        dest = agent.dest

        route = ox.shortest_path(self.G, orig, dest, weight='cost')
        agent.route = route

    def plot_graph(self):
        from tsunami.config import DATA_DIR

        #coastline = gpd.read_file(os.path.join(DATA_DIR, "coastline.gpkg"))
        #buildings = gpd.read_file(os.path.join(DATA_DIR, "buildings.gpkg"))
        #tourism = gpd.read_file(os.path.join(DATA_DIR, "tourism.gpkg"))

        nc = []
        for n in self.G.nodes:
            n_agents = len(self.G.nodes[n]["agents"])
            # print(self.G.nodes[n])
            # print(n_agents)

            if n_agents < 10:
                nc.append("green")
            elif n_agents < 50:
                nc.append("yellow")
            elif n_agents < 150:
                nc.append("orange")
            elif n_agents < 300:
                nc.append("red")
            else:
                nc.append("#8a0900")

        # ns = [0 if len(self.G.nodes[n]["agents"]) == 0 else 15 for n in self.G.nodes]
        ns = [len(self.G.nodes[n]["agents"]) for n in self.G.nodes]
        plot_graph(self.G, node_size=ns, node_color=nc, show=True, padding=0)

