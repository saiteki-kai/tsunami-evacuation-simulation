from time import time


class Pedestrian:
    def __init__(self, name, type):
        self.name = name
        self.type = type  # the type of the agent (Resident, Tourist)
        self.dead = False
        self.evacuated = False

        self.orig_node = None  # origin node
        self.dest_node = None  # destination node
        self.route = None  # list of nodes of the path from origin to destination

        self.next_node = None  # the next node in the path
        self.curr_node = None  # current node position
        self.pos = None  # spatial current position at the start or on the current edge

        self.link = {}  # current link with enter time

    def set_initial_node(self, node):
        self.orig_node = node
        self.curr_node = node

    def set_next_node(self):
        self.next_node = self.__get_next_node()

    def update_next_node(self):
        self.curr_node = self.next_node
        self.next_node = self.__get_next_node()

    def __get_next_node(self):
        next_node_index = self.route.index(self.curr_node) + 1
        if next_node_index < len(self.route):
            return self.route[next_node_index]

    def update_pos(self, time_step):
        link = self.link["link"]
        length = link.l
        meter_per_step = link.v * time_step
        k = meter_per_step * 100 / length

        if 0 < int(k) < 100:
            x_diff = self.next_node["x"] - self.curr_node["x"]
            y_diff = self.next_node["y"] - self.curr_node["y"]

            if x_diff != 0 and y_diff != 0:
                x_offset = x_diff / abs(x_diff) * k
                y_offset = y_diff / abs(y_diff) * k
                self.pos = (self.curr_node["x"] + x_offset, self.curr_node["y"] + y_offset)
            else:
                print("è un problema...")

    def kill(self):
        self.dead = True

    def set_link(self, link):
        self.link = {"enter_time": time(), "link": link}
