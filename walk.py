
import json
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
from random import randint
from networkx.readwrite import adjacency_graph

from spanning_trees import explore_random
from autographs.faces import HalfEdge
from make_graph import construct_graph_from_file

"""
This script runs a variable-length tree walk on the provided graph and
corresponding shapefile. Then, it generates face-colored maps as svgs.
"""

# Default values for finding plans.
num_plans = 1
delta = 0.2

# Paths to files.
graph_path = "./data/MS_geodata_geopos.json"
shp_path = "./data/MS_BLKGRP_DEM_ADJ/MS_BLKGRP_DEM_ADJ.shp"

# Demographic data column names.
total_pop_column = "POP10"
black_pop_column = "POPB"

with open(graph_path, "r") as f:
    graph = adjacency_graph(json.loads(f.read()))

# Create an ensemble of districting plans.
ensemble = [explore_random(graph, 1, 4, delta=delta)[0] for i in range(num_plans)]

# The set of interesting plans.
interesting = []

# Determine which plans have better (or weirder) representation
# for the black population. If they have find which ones are
# reasonable, and shove them into a list.
for plan in ensemble:
    # Create a list of representation percentages.
    representation = []

    for district in plan:
        total = sum(list(nx.get_node_attributes(district, total_pop_column).values()))
        black = sum(list(nx.get_node_attributes(district, black_pop_column).values()))
        representation.append(black / total)

    # If more than two districts have a >50% black population, save it.
    count = 0
    for district in representation:
        if district > 0.5:
            count += 1

        if count == 2:
            interesting.append((plan, representation))
            break

    # If more than three districts have a >38% black population, save it, too.
    count = 0
    for district in representation:
        if district > 0.38:
            count += 1

        if count == 3:
            interesting.append((plan, representation))
            break

    # Do this when testing.
    interesting.append((plan, representation))
    
# Go through the interesting plans and make shapefiles of them.
for index, pair in enumerate(interesting):
    # Load the shapefile.
    adj_df = gpd.read_file(shp_path)
    adj_df.set_index("GEOID")
    adj_df["CD"] = [0 for i in range(0, len(adj_df["GEOID"]))]
    adj_df["REP"] = [0 for i in range(0, len(adj_df["GEOID"]))]

    plan = pair[0]
    representation = pair[1]

    # Go over each district and augment the shapefile with the correct district
    # assignments.
    assignment = 0
    for district in plan:
        # Go over the tracts and assign each vertex a district!
        for tract in district.nodes:
            adj_df.loc[adj_df["GEOID"] == tract, "CD"] = assignment
            adj_df.loc[adj_df["GEOID"] == tract, "REP"] = representation[assignment]
        
        # Increase the district assignment label.
        assignment += 1

    adj_df.to_file(f"./map_shapefiles/{index}.shp")

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

# Get the faces of the plans!
for i, info in enumerate(interesting):
    # Create a new HalfEdge data structure to find faces.
    he = HalfEdge(f"./map_shapefiles/{i}.shp")

    # Create a mapping from index -> geoid.
    df = gpd.read_file(f"./map_shapefiles/{i}.shp")
    
    # Pick a color scheme.
    color_map = color_maps[randint(0, 2)]
    
    # Initialize a variable to count the number of big faces.
    count = 0

    for face in he.faces:
        # Get list(s) of the bounding centroids' coordinates.
        x = [edge.head.x for edge in face]
        y = [edge.head.y for edge in face]

        # For each edge in the face, get the congressional district assignment.
        cds = set()

        # Go over the edges and add representation stuff.
        for edge in face:
            head = edge.head
            tail = edge.tail
            cds.add(df["CD"][head.label])

            # Check whether the edge connects vertices in the same district.
            if df["CD"][head.label] == df["CD"][tail.label]:
                color = color_map[df["CD"][head.label]]
                plt.plot([head.x, tail.x], [head.y, tail.y], c=f"xkcd:{color}", linewidth=1)

        cds = list(cds)

        # If the face is interior to the component, color it. Also, color its edges
        if len(cds) == 1:
            cd = cds[0]
            plt.fill(x, y, c=f"xkcd:{color_map[cd]}", linewidth=2, edgecolor="w", closed=True)

        if len(face) > 10 and len(cds) == 1:
            cd = cds[0]
            count += 1
            plt.fill(x, y, c=f"xkcd:{color_map[cd]}", linewidth=2, edgecolor="w", closed=True, label=cd)

    plt.axis("off")
    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=count, mode="expand", borderaxespad=0.)
    plt.savefig(f"./maps/{info[1]}.svg", dpi=100000)
    plt.close()