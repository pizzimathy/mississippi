
import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.readwrite import adjacency_graph
from random import randint

from autographs.faces import HalfEdge

"""
Imports a seeded plan and makes a pretty map of it.
"""

# Load the district assignment into pandas.
df = pd.read_csv("./data/seeds/MS_2.csv")

# Load the shapefile and make a blank column.
shp = gpd.read_file("./data/MS_BLKGRP_DEM_ADJ/MS_BLKGRP_DEM_ADJ.shp")
shp["CD"] = [0 for i in range(len(shp))]

# Assign the congressional districts!
for index, row in df.iterrows():
    cd = row["CD"]
    geoid = row["GEOID"][9:]
    shp.loc[shp["GEOID"] == geoid, "CD"] = cd

# Save the shapefile.
shp.to_file("./map_shapefiles/seeded.shp")

# Find faces!

# Create a few color maps.
blue_green = {
    0: "light blue",
    1: "blue",
    2: "yellow green",
    3: "aqua"
}

pastel_hues = {
    0: "pink",
    1: "magenta",
    2: "dark blue",
    3: "cyan"
}

underwater = {
    0: "plum",
    1: "aquamarine",
    2: "blue",
    3: "coral"
}

color_maps = [blue_green, pastel_hues, underwater]

# Create a new HalfEdge data structure to find faces.
he = HalfEdge(f"./map_shapefiles/seeded.shp")

# Create a mapping from index -> geoid.
df = gpd.read_file(f"./map_shapefiles/seeded.shp")

# Pick a color scheme.
color_map = color_maps[randint(0, 2)]

for face in he.faces:
    
    # Get list(s) of the bounding centroids' coordinates.
    x = [edge.head.x for edge in face]
    y = [edge.head.y for edge in face]

    # For each edge in the face, get the congressional district assignment.
    cds = set()

    # Go over the edges and add representation stuff.
    for edge in face:
        head = edge.head
        index = head.label

        # Have to do a weird thing here because some subdivisions weren't given
        # a district assignment.
        cd = df["CD"][index]
        if cd > 0:
            cds.add(cd - 1)

    # If the face is interior to the component, color it. Also, color its edges.
    if len(cds) == 1:
        plt.fill(x, y, c=f"xkcd:{color_map[cds.pop()]}", linewidth=2, edgecolor="w", closed=True)

plt.axis("off")
plt.savefig(f"./maps/seeded.svg", dpi=100000)
plt.close()
