from queue import Queue

# TEST

capacity = 5

q = Queue(capacity)

if q.qsize() < capacity:
    q.put("AO")
else:
    print("FULL!")

print(q.get())

import networkx as nx
import osmnx as ox

# Utils


def set_attribute(G, edge, attr, value):
    u, v, key = edge
    G[u][v][key][attr] = value


# TODO: put function in a class

def init_queues(G):
    edges = ox.graph_to_gdfs(G, nodes=False)
    edges["queues"] = []
    for e in edges:
        # compute capacity
        # capacity = e["area"] / person_size
        edges["queues"].append(Queue(maxsize=5))
    nx.set_edge_attributes(G, edges["queues"], "queue")


def init_population(G):
    for u, d in G.nodes(data=True):
        pass


def init_edges(G):
    init_queues(G)
    init_population(G)
