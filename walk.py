
import json
import networkx as nx
from networkx.readwrite import adjacency_graph

from spanning_trees import explore_random

with open("./data/graph_data.json", "r") as f:
    graph = adjacency_graph(json.loads(f.read()))

# Create an ensemble of districting plans.
ensemble = [explore_random(graph, 1, 4, delta=0.2)[0] for i in range(0, 100)]

# The set of interesting plans.
interesting = []

# Determine which plans have better (or weirder) representation
# for the black population. If they have find which ones are
# reasonable, and shove them into a list.
for plans in ensemble:
    # Create a list of representation percentages.
    representation = []

    for plan in plans:
        total = sum(list(nx.get_node_attributes(plan, "POP10").values()))
        black = sum(list(nx.get_node_attributes(plan, "BPOP").values()))
        representation.append(black / total)

    print(representation)

    # If more than two districts have a >60% black population, save it.
    count = 0
    for district in representation:
        if district > 0.6:
            count += 1

        if count == 2:
            interesting.append(representation)
            break

    # If more than three districts have a >41% black population, save it, too.
    count = 0
    for district in representation:
        if district > 0.41:
            count += 1

        if count == 3:
            interesting.append(representation)
            break
