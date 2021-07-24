from queue import Queue
from time import time

from tsunami.simulation.pedestrian import Pedestrian


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

    def dequeue(self, k, T):
        if self.queue.empty():
            return []

        agents = []
        for _ in range(int(self.q)):
            if not self.queue.empty():
                agent = self.queue.queue[0]
                can_leave = time() + k * T > agent.link["enter_time"] + self.get_travel_time()

                # print(
                #    f"{time() + k * T} > {agent.link['enter_time'] + self.get_travel_time()} => {can_leave}"
                # )

                if can_leave:
                    a = self.queue.get()
                    agents.append(a)

        return agents

    def print_queue(self):
        print(self.queue.queue)

    def get_queue_used(self):
        return round(self.queue.qsize() / self.c * 100, 2)

    def __str__(self) -> str:
        return f"capacity: {self.c}, q: {self.q}, queue: {self.queue}"


def choice_link(graph, agent: Pedestrian):
    min_c = float("inf")
    min_e = None

    for e in graph.out_edges(agent.curr_node["id"], keys=True):
        c = graph.edges[e]["cost"]

        if c < min_c:
            min_c = c
            min_e = e

    return min_e
