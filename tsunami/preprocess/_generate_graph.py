#!env/bin/python3
import json


class Graph:
    def __init__(self, N):
        self.N = N
        self.graph = {}

    def add_node(self, value):
        self.graph[value] = []

    def add_edge(self, a, b):
        if b not in self.graph[a]:
            self.graph[a].append(b)

    def print_agraph(self):
        for i in self.graph:
            if len(self.graph[i]) > 4:
                print("Vertex " + str(i) + ":", end="")
                for j in self.graph[i]:
                    print(" -> {}".format(j), end="")
                print(" \n")


from pyvis.network import Network

net = Network()

with open("data.json") as f:
    data = json.load(f)
    nodes = data["nodes"]
    print("ciao")

    # graph = Graph(len(nodes))

    for i in nodes:
        # graph.add_node(i)
        # n = nodes[i]
        net.add_node(i)

    print("ways")
    for i in data["ways"]:
        way = data["ways"][i]
        print(i)

        if i == "112121164":
            print("ciao")
            print(way["nodes"])

        for k in range(len(way["nodes"]) - 1):
            id1 = way["nodes"][k]
            id2 = way["nodes"][k + 1]

            # graph.add_edge(id1, id2)
            net.add_edge(id1, id2)

            if i == "112121164":
                print(id1, id2)

    # graph.print_agraph()
    net.enable_physics(True)
    net.show('mygraph.html')
