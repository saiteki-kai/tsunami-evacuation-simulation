import os

import geopandas as gpd
import osmnx as ox

from tsunami.config import DATA_DIR
from tsunami.simulation.model import EvacuationModel
from tsunami.simulation.plot import ModelViewer

G = ox.load_graphml(os.path.join(DATA_DIR, "graph.xml"))

population = gpd.read_file(os.path.join(DATA_DIR, "population.gpkg"))

# TEST
population = population.head(1)
population["population"][0] = 1

model = EvacuationModel(G, 5, 5)
model.init_state(population=population, shelters=None, tsunami=None)

model.agents[0].orig = list(G)[10]
model.agents[0].dest = list(G)[0]
model.compute_route(model.agents[0])
print(model.agents[0].route)

model.run_iteration()

viewer = ModelViewer(model)
viewer.plot_street()
# viewer.plot_population()
# fig, ax = viewer.plot_route(model.agents[0].route, ax)
