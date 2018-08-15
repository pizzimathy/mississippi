
import json
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
from networkx.readwrite import adjacency_graph

from spanning_trees import explore_random
from autographs.faces import HalfEdge
from make_graph import construct_graph_from_file

with open("./data/graph_data.json", "r") as f:
    graph = adjacency_graph(json.loads(f.read()))

# Create an ensemble of districting plans.
num_plans = 10
delta = 0.1
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
        total = sum(list(nx.get_node_attributes(district, "POP10").values()))
        black = sum(list(nx.get_node_attributes(district, "BPOP").values()))
        representation.append(black / total)

    """
    # If more than two districts have a >60% black population, save it.
    count = 0
    for district in representation:
        if district > 0.6:
            count += 1

        if count == 2:
            interesting.append(plan)
            break

    # If more than three districts have a >41% black population, save it, too.
    count = 0
    for district in representation:
        if district > 0.41:
            count += 1

        if count == 3:
            interesting.append(plan)
            break
    """
    
    # Just do this for now.
    interesting.append((plan, representation))

# Go through the interesting plans and make shapefiles of them.
for index, pair in enumerate(interesting):
    # Load the shapefile.
    adj_df = gpd.read_file("./data/tl_2016_28_tract_merged/tl_2016_28_tract_merged.shp")
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
        
        assignment += 1

    adj_df.to_file(f"./map_shapefiles/{index}.shp")

# Get the faces of the plans!
for i in range(len(interesting)):
    # Create a new HalfEdge data structure to find faces.
    he = HalfEdge(f"./map_shapefiles/{i}.shp")

    # Create a mapping from index -> geoid.
    df = gpd.read_file(f"./map_shapefiles/{i}.shp")

    for face in he.faces:
        # Get list(s) of the bounding centroids' coordinates.
        x = [edge[0].x for edge in face]
        y = [edge[0].y for edge in face]

        # For each edge in the face, get the congressional district assignment
        # and the representation for that district.
        cds = set()
        representation_percent = set()

        for edge in face:
            head = edge[0]
            index = head.label
            cds.add(df["CD"][index])
            representation_percent.add(df["REP"][index])

        if len(cds) == 1:
            plt.fill(x, y, "black", alpha=representation_percent.pop(), linewidth=1)

    plt.axis("off")
    plt.savefig(f"./maps/{i}.svg", dpi=10000)
    plt.close()