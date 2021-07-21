import os

import geopandas as gpd
import osmnx as ox

from tsunami.config import DATA_DIR
from tsunami.simulation.model import EvacuationModel
from tsunami.simulation.plot import ModelViewer


def compute_route_stats(agent):
    path = agent.route

    total_travel_time = 0
    total_length = 0
    avg_velocity = 0
    for u, v in zip(path[0:], path[1:]):
        edge_data = G.get_edge_data(u, v)
        costs = [edge_data[edge]['cost'] for edge in edge_data]

        min_cost = min(costs)
        min_idx = costs.index(min_cost)
        min_length = edge_data[min_idx]['length']

        velocity = edge_data[min_idx]['link'].v

        avg_velocity += velocity
        total_travel_time += min_cost
        total_length += min_length
    total_travel_time /= 3600
    total_length /= 1000
    avg_velocity /= len(path) - 1
    print(
        f"travel_time: {total_travel_time:.2f}h\t length: {total_length:.2f}Km\t average velocity: {avg_velocity:.2f}m/s")


G = ox.load_graphml(os.path.join(DATA_DIR, "graph.xml"))

population = gpd.read_file(os.path.join(DATA_DIR, "districts.gpkg"))

# TEST
# population = population.head(1)
# population["population"][0] = 1

model = EvacuationModel(G, 5, 10)
model.init_state(population=population, shelters=None, tsunami=None)

a0 = model.agents[0]
a0.orig = list(G)[13]
a0.dest = list(G)[1]

model.compute_route(a0)
compute_route_stats(a0)

# model.run_iteration()

model.compute_route(a0)
compute_route_stats(a0)

viewer = ModelViewer(model)
# viewer.interactive_graph()
# viewer.plot_street()
# viewer.plot_population(save=True)
viewer.plot_route(a0.route, save=True, show=False)
