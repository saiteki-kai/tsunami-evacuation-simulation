import os

import osmnx as ox

from tsunami.config import DATA_DIR
from tsunami.simulation.model import EvacuationModel

G = ox.load_graphml(os.path.join(DATA_DIR, "graph.xml"))

model = EvacuationModel(G)
model.init_state(population=None, shelters=None, tsunami=None)
# model.run_iteration()
