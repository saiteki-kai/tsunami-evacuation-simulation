import random

import networkx as nx
import numpy as np
import osmnx as ox
from time import time

from tsunami.simulation.link import Link, choice_link
from tsunami.simulation.pedestrian import Pedestrian
from tsunami.utils.roads import get_width


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

    def __finished(self):
        if self.ST is not None:
            return self.k >= int(self.ST // self.T)

        return self.evacuated_agents + self.dead_agents != self.total_agents

    def __add_population(self, population):
        print("init population")
        self.total_agents = population['population'].sum()

        nx.set_node_attributes(self.G, {n: [] for n in self.G.nodes}, "agents")

        # Add Residents
        for p in range(len(population)):
            name = population["name"][p]
            quantity = population["population"][p]
            polygon = population["geometry"][p]

            agents = [Pedestrian(f"{name}#{i}", "resident") for i in range(quantity)]
            self.agents.extend(agents)

            gdf_nodes = ox.graph_to_gdfs(self.G, edges=False, fill_edge_geometry=False)
            nodes_indices = gdf_nodes[gdf_nodes.geometry.within(polygon)].index.values
            K = min(quantity, len(nodes_indices))  # number of nodes to divide the population into

            print(f"K: {K:3d}\t population: {quantity:4d}\t n_indices: {len(nodes_indices)}")

            if K == 0:
                continue

            partitions = np.array_split(agents, K)

            for k in range(K):
                if len(nodes_indices) <= quantity:
                    idx = k
                else:
                    idx = random.randint(0, len(nodes_indices) - 1)

                n = nodes_indices[idx]

                # inizializzo la posizione degli agenti
                for agent in partitions[k]:
                    agent.curr_node = self.G.nodes[n]
                    agent.pos = agent.curr_node["x"], agent.curr_node["y"]

        # Add Tourists

    def __add_shelters(self, shelters):
        pass

    def __add_tsunami(self, tsunami):
        pass

    def __assign_destinations(self):
        print("init destinations")
        # for n in self.agents:
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
        print("init queues")
        for e in self.G.edges:
            edge = self.G.edges[e]

            length = edge["length"]
            width = get_width(edge["highway"], edge["lanes"] if "lanes" in edge else 0)
            area = length * width

            link = Link(length, width, area)

            edge["link"] = link
            edge["cost"] = link.get_travel_time()

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

        self.update_graph()

        for curr_edge in self.G.edges:
            edge = self.G.edges[curr_edge]
            _, v, _ = curr_edge

            if "link" in edge:
                can_leave = lambda x: time() + self.k * self.T > x.link["enter_time"] + self.get_travel_time()
                for agent in self.agents:

                    print(f"{time() + self.k * self.T} > \
                        {agent.link['enter_time'] + self.get_travel_time()} => {can_leave(agent)}")

                    if can_leave(agent):
                        edge["link"].dequeue(agent) # dequeue
                        agent.update_next_node(self.G.nodes[v]) # update next node
                    else:
                        # move agent position
                        agent.update_pos(self.T)

    def run_iteration(self):
        print("# ---------------------------------------------------")

        while not self.__finished():
            self.step()
            self.k += 1

        print("# ---------------------------------------------------")

    def update_graph(self):
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

    def compute_route(self, agent):
        if agent.dest is None:
            raise ValueError("Agent destination not specified!")

        orig = agent.orig
        dest = agent.dest

        route = ox.shortest_path(self.G, orig, dest, weight='cost')
        agent.route = route
