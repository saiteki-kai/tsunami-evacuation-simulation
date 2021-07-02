class Inhabitant:
    def __init__(self):
        self.edge = None  # position on graph
        self.dead = False

    def move(self, next_edge):
        self.edge = next_edge

    def kill(self):
        self.dead = True
