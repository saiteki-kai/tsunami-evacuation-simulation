from time import time


class Pedestrian:
    def __init__(self, name, type):
        self.name = name
        self.type = type # the type of the agent (Resident, Tourist)
        self.dead = False
        self.evacuated = False

        self.orig_node = None # origin node
        self.dest_node = None # destination node
        self.route = None # path from origin to destination
        self.curr_node_index = None # index of the current node in the route list

        self.next_node = None # the next node in the path
        self.curr_node = None # current node position
        self.pos = None # spatial current position at the start or on the current edge

    def set_initial_node(self, node):
        self.orig_node = node
        self.curr_node = node

    def move(self, link, period):
        length = link.l
        meter_per_step = link.__MAX_SPEED * period
        k = meter_per_step * 100 / length

        if int(k) == 100:
            self.curr_node = self.next_node
            self.next_node = self.route[self.curr_node_index + 1]
        else:
            x_diff = self.next_node["x"] - self.curr_node["x"]
            y_diff = self.next_node["y"] - self.curr_node["y"]
            x_offset = x_diff / abs(x_diff) * k
            y_offset = y_diff / abs(y_diff) * k
            self.pos = self.curr_node["x"] + x_offset, self.curr_node["y"] + y_offset

    def kill(self):
        self.dead = True

    #def set_link(self, link):
    #    self.link = {"enter_time": time(), "link": link}
