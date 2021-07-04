from queue import Queue

import networkx as nx
import osmnx as ox


class EvacuationModel:
    def __init__(self, graph):
        self.G = graph
        self.total_agents = 0
        self.evacuated_agents = 0
        self.dead_agents = 0

    def init_state(self, population, shelters, tsunami):
        self.G = self.__init_queues()
        self.G = self.__add_population(population)
        self.G = self.__add_shelters(shelters)
        self.G = self.__add_tsunami(tsunami)

        for u, v, d in self.G.edges(data=True):
            print(d["queue"])

    def reset_state(self):
        self.total_agents = 0
        self.evacuated_agents = 0
        self.dead_agents = 0

    def step(self):
        pass

    def run_iteration(self):
        while not self.__finished():
            self.step()

    def __finished(self):
        return self.evacuated_agents + self.dead_agents != self.total_agents

    def __add_population(self, population):
        # for u, d in self.G.nodes(data=True):
        #    pass
        self.total_agents = 5
        return self.G

    def __add_shelters(self, shelters):
        return self.G

    def __add_tsunami(self, tsunami):
        return self.G

    def __init_queues(self):
        edges = ox.graph_to_gdfs(self.G, nodes=False, fill_edge_geometry=False)

        queues = {}
        for k in self.G.edges():
            # compute capacity
            # capacity = e["area"] / person_size
            queues[k] = Queue(maxsize=5)

        nx.set_edge_attributes(self.G, values=queues, name="queue")

        return self.G
