import os

import osmnx as ox
import geopandas as gpd

from tsunami.config import DATA_DIR
from tsunami.simulation.model import EvacuationModel

G = ox.load_graphml(os.path.join(DATA_DIR, "graph.xml"))

population = gpd.read_file(os.path.join(DATA_DIR, "population.gpkg"))

model = EvacuationModel(G, 5, 100)
model.init_state(population=population, shelters=None, tsunami=None)
# model.run_iteration()
