from queue import Queue
from time import time


class Link:
    def __init__(self, length, min_width, area):
        self.__MAX_SPEED = 1.66  # max free flow speed # [m / s]
        self.__MAX_DENSITY = 5.4  # max density [ped / m^2]
        self.__MAX_CAPACITY = 1.33  # max capacity [ped / (m * s)]

        self.l = length
        self.w = min_width
        self.a = area

        self.v = self.__MAX_SPEED  # initial velocity [m / s]

        self.c = int(self.a * self.__MAX_DENSITY)  # storage capacity [ped]
        self.q = self.w * self.__MAX_CAPACITY  # flow capacity [ped / s]
        self.t = self.l / self.__MAX_SPEED  # free speed travel time [s]

        self.queue = Queue(maxsize=self.c)

    def get_travel_time(self):
        return self.t

    def update_travel_time(self):
        self.t = self.l / self.v
        return self.t

    def update_velocity(self):
        K = self.q / self.c * self.l
        p = self.queue.qsize() / self.c
        self.v = min(self.__MAX_SPEED, K / p)

        return self.v

    def enqueue(self, agent):
        if self.queue.qsize() < self.queue.maxsize:
            self.queue.put(agent)
            return True
        else:
            return False

    def dequeue(self, agent):
        if self.queue.empty():
            return []

        if not self.queue.empty():
            agent = self.queue.queue[0]
            a = self.queue.get()

    def print_queue(self):
        print(self.queue.queue)

    def get_queue_used(self):
        return round(self.queue.qsize() / self.c * 100)

    def __str__(self) -> str:
        return f"capacity: {self.c}, q: {self.q}, queue: {self.queue}"


def choice_link(graph, curr_node):
    if "agents" in graph.nodes[curr_node] and len(graph.nodes[curr_node]["agents"]) > 0:

        out_nodes = graph.out_edges(curr_node, keys=True)

        if len(out_nodes) < 1:
            return None

        min_t = float("inf")
        min_e = None

        for e in out_nodes:
            link = graph.edges[e]["link"]
            t = link.get_travel_time()

            if t < min_t:
                min_t = t
                min_e = e

        agent = graph.nodes[curr_node]["agents"].pop()
        agent.set_link(graph.edges[min_e]["link"])

        graph.edges[min_e]["link"].enqueue(agent)
        return min_e
    return None
