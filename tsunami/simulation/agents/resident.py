from time import time


class Resident:
    def __init__(self, name):
        self.name = name
        self.link = {}
        self.edge = None
        self.dead = False
        self.evacuated = False

    def move(self, next_edge):
        self.edge = next_edge

    def kill(self):
        self.dead = True

    def set_link(self, link):
        self.link = {"enter_time": time(), "link": link}
