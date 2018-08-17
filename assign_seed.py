
from networkx.readwrite import adjacency_data, adjacency_graph
import networkx as nx
import pandas as pd
import json

"""
This script assigns congressional districts to Mississippi's blocks based on a
seed from Districtr.
"""

# Load in the districting assignment.
df = pd.read_csv("./data/seeds/MS_priority.csv")

# Load in the graph.
with open("./data/MS_geodata_geopos.json", "r") as f:
    graph = adjacency_graph(json.loads(f.read()))

# Iterate over the vertices, assigning their congressional districts
# as we go!
for vertex, data in graph.nodes(data=True):
    adj_geoid = "1500000US" + vertex
    cd = df.loc[df["GEOID"] == adj_geoid]["CD"]
    graph.nodes[vertex]["CD"] = int(cd)

# Write back to the graph.
with open("./data/MS_geodata_geopos.json", "w") as f:
    f.write(json.dumps(adjacency_data(graph)))
