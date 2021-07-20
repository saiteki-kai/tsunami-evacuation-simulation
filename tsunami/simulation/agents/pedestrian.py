from time import time


class Pedestrian:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.link = {}
        self.edge = None
        self.dead = False
        self.evacuated = False

        self.orig = None
        self.dest = None
        self.route = None

    def move(self, next_edge):
        self.edge = next_edge

    def kill(self):
        self.dead = True

    def set_link(self, link):
        self.link = {"enter_time": time(), "link": link}
