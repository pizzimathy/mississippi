
import json
import geopandas as gpd
import networkx as nx
from networkx.readwrite import adjacency_data

from make_graph import construct_graph_from_df

"""
Takes in data from a shapefile, generates a dual graph, and shoves data into the
graph for later use by the tree walk.
"""

# Generate a simple rook adjacency graph augmented with centroids.
tracts = gpd.read_file("./data/tl_2016_28_tract_merged/tl_2016_28_tract_merged.shp")

# Assign centroids, and convert them to lists.
centroids = tracts.centroid
geopos = [(centroid.x, centroid.y) for centroid in centroids]
tracts["geopos"] = geopos

# Make the graph!
print("Constructing graph.")
graph = construct_graph_from_df(
    tracts,
    id_col="GEOID",
    pop_col="POP10",
    area_col="ALAND",
    cols_to_add=["BPOP", "geopos"]
)

with open("./data/graph_data.json", "w") as f:
    f.write(json.dumps(adjacency_data(graph)))