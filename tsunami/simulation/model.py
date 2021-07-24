import random

import networkx as nx
import numpy as np
import osmnx as ox

from tsunami.simulation.link import Link, choice_link
from tsunami.simulation.pedestrian import Pedestrian
from tsunami.utils.roads import get_width


class EvacuationModel:
    def __init__(self, graph: nx.MultiDiGraph, time_step, simulation_time=None):
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

        l = 0
        # Add Residents
        for p in range(len(population)):
            name = population["name"][p]
            quantity = population["population"][p]
            polygon = population["geometry"][p]

            agents = [Pedestrian(f"{name}#{i}", "resident") for i in range(quantity)]

            gdf_nodes = ox.graph_to_gdfs(self.G, edges=False, fill_edge_geometry=False)
            nodes_indices = gdf_nodes[gdf_nodes.geometry.within(polygon)].index.values
            K = min(quantity, len(nodes_indices))  # number of nodes to divide the population into

            print(f"K: {K:3d}\t population: {quantity:4d}\t n_indices: {len(nodes_indices)}")

            if K == 0:
                continue
            else:
                self.agents.extend(agents)

            partitions = np.array_split(agents, K)

            for k in range(K):
                if len(nodes_indices) <= quantity:
                    idx = k
                else:
                    idx = random.randint(0, len(nodes_indices) - 1)

                n = nodes_indices[idx]

                # initialize agent's position and first link
                for agent in partitions[k]:
                    agent.set_initial_node(self.G.nodes[n])
                    agent.pos = (agent.curr_node["x"], agent.curr_node["y"])

                    # set initial edge
                    edges = self.G.out_edges(n, keys=True)
                    link = self.G.edges[list(edges)[0]]["link"]
                    agent.set_link(link)
                    link.enqueue(agent)

                    l = l + 1

        print(f"{l}/{len(self.agents)}")

        # Add Tourists

    def __add_shelters(self, shelters):
        pass

    def __add_tsunami(self, tsunami):
        pass

    def __assign_destinations(self):
        print("init destinations")
        for agent in self.agents:
            agent.dest_node = self.G.nodes[100]
            # agent.dest_node = self.__choice_shelter(agent.orig_node)

    def __choice_shelter(self, node):
        gdf = ox.graph_to_gdfs(self.G, edges=False)
        gdf.query()
        return None

    def __add_routes(self):
        print("init routes")
        self.compute_routes()

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

        # update position of each agent in the queue
        for agent in self.agents:
            if agent.next_node is None:
                print("Boh...")
                continue
            agent.update_pos(self.T)

        for e in self.G.edges:
            edge = self.G.edges[e]

            # dequeue agents that can leave
            agents = edge["link"].dequeue(self.k, self.T)

            if agents is not None and len(agents) > 0:
                print(f"dequeue ({[a.name for a in agents]})")

            # update agent's curr_edge
            for agent in agents:
                min_e = choice_link(self.G, agent)

                if min_e is None:
                    continue

                _, v, _ = min_e
                agent.curr_node = self.G.nodes[v]

                print(f"enqueue ({agent.name})")
                agent.set_link(self.G.edges[min_e]["link"])
                self.G.edges[min_e]["link"].enqueue(agent)

        # update Link objects
        for e in self.G.edges:
            edge = self.G.edges[e]

            if "link" not in edge:
                continue

            link = edge["link"]

            # update only if any agents is present in the edge
            if link.queue.qsize() > 0:
                # print(f"update link of {e} {link.queue.qsize()}")

                link.update_velocity()
                new_cost = link.update_travel_time()
                edge["cost"] = new_cost

                print((
                    f"velocity: {link.v:.2f} m/s\t"
                    f"travel time: {link.t:.2f}s\t"
                    f"queue: [{e}] {link.get_queue_used()}% {link.queue.qsize()}"
                ))

    def run_iteration(self):
        print("# ---------------------------------------------------")

        while not self.__finished():
            self.step()
            self.k += 1

        print("# ---------------------------------------------------")

    def compute_routes(self):
        agents = [a for a in self.agents
                  if a.orig_node is not None
                  and a.dest_node is not None
                  and "id" in a.orig_node
                  and "id" in a.dest_node]

        orig = [a.orig_node["id"] for a in agents]
        dest = [a.dest_node["id"] for a in agents]

        routes = ox.shortest_path(self.G, orig, dest, weight='cost')

        for i in range(len(routes)):
            agents[i].route = [self.G.nodes[node_id] for node_id in routes[i]]
            agents[i].set_next_node()

    def compute_route(self, agent):
        if agent.dest_node is None:
            raise ValueError("Agent destination not specified!")

        orig = agent.orig_node["id"]
        dest = agent.dest_node["id"]

        route = ox.shortest_path(self.G, orig, dest, weight='cost')
        route = [self.G.nodes[node_id] for node_id in route]
        agent.route = route
