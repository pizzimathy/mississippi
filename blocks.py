
import json
import networkx as nx
import geopandas as gpd
from networkx.readwrite import adjacency_graph, adjacency_data

"""
This script is designed to take in a graph with bad geopositioning data,
find the corresponding geographic point, then give the graph good
geopositioning data. Furthermore, it saves both the graph and the adjusted
shapefile, so they're easily available for future use.
"""

# Import the graph from the json file.
with open("./data/MS_geodata.json") as f:
    graph = adjacency_graph(json.loads(f.read()))

# Load the shapefile with the geometries on it.
blocks = gpd.read_file("./data/MS_BLKGRP_DEM/MS_BLKGRP_DEM.shp")

# Find the centroids for the blocks.
centroids = blocks.centroid
geopos = [str((centroid.x, centroid.y)) for centroid in centroids]
blocks["geopos"] = geopos

# Set the index of the shapefile to be the geoid column.
blocks["GEOID"] = [geoid[9:] for geoid in blocks["GEOID"]]
blocks.set_index("GEOID", inplace=True)

# Iterate over each row and select vertices by matching geoids. Then, assign the
# proper geolocation.
for block in blocks.itertuples():
    adj_geoid = block[0]
    vertex = [v for v, data in graph.nodes(data=True) if adj_geoid == v][0]
    graph.nodes[vertex]["geopos"] = block[-1]

# Save the shapefile so I can use it later, but reset the index column.
blocks["index"] = list(range(len(blocks["geopos"])))
blocks["GEOID"] = blocks.index.values
blocks.set_index("index", inplace=True)
blocks.to_file("./data/MS_BLKGRP_DEM_ADJ/MS_BLKGRP_DEM_ADJ.shp")

# Save the graph.
with open("./data/MS_geodata_geopos.json", "w") as f:
    f.write(json.dumps(adjacency_data(graph)))
