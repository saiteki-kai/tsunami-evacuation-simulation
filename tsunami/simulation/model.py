import networkx as nx

from tsunami.simulation.link import Link, choice_link
from tsunami.utils.roads import get_width


class EvacuationModel:
    def __init__(self, graph, time_step, simulation_time=None):
        self.G = graph
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
            edge = choice_link(self.G, curr_node)

            if edge is not None:
                link = self.G.edges[edge]["link"]

                link.update_velocity()
                link.update_travel_time()

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
        self.total_agents = 5
        nx.set_node_attributes(self.G, [], "agents")
        # for u, d in self.G.nodes(data=True):
        #    pass

    def __add_shelters(self, shelters):
        pass

    def __add_tsunami(self, tsunami):
        pass

    def __init_queues(self):
        for e in self.G.edges:
            edge = self.G.edges[e]

            length = edge["length"]
            width = get_width(edge["highway"], edge["lanes"] if "lanes" in edge else 0)
            area = length * width

            edge["link"] = Link(length, width, area)
