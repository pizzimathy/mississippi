
import networkx as nx
import matplotlib.pyplot as plt

import spanning_trees.Broder_Wilson_algorithms as bwa
from spanning_trees import explore_random

"""
Generating pretty pictures of trees, stealing from Lorenzo's visualization_tools
package.
"""

# Specify the number of cuts to make and generate a toy grid graph.
cuts = 4
graph = nx.grid_graph([10*cuts, 10*cuts])

# Fake the data on the graph.
for vertex in graph:
    graph.nodes[vertex]["geopos"] = vertex
    graph.nodes[vertex]["POP10"] = 1
    
# Find a partition and find a tree for that partition.
partition = explore_random(graph, 1, cuts, divide_and_conquer=True, equi=False, with_walk=False)[0]
tree = bwa.random_spanning_tree_wilson(graph)
geopos = nx.get_node_attributes(tree, "geopos")

# Color the nodes.
for i in range(len(partition)):
    for vertex in partition[i].nodes():
        graph.nodes[vertex]["district"] = i
        graph.nodes[vertex]["pos"] = graph.nodes[vertex]["geopos"]

# Label the edges.
for edge in graph.edges():
    graph.edges[edge]["tree"] = 0

color_map = {
    0: "r",
    1: "b",
    2: "y",
    3: "g"
}

# Iterate over each edge and color them.
for edge in tree.edges():
    # Get the head and tail of each edge. Then, check if they're in the same
    # district; if they are, color the edge accordingly. Otherwise, don't.
    head, tail = edge[0], edge[1]
    x, y = [head[0], tail[0]], [head[1], tail[1]]

    if graph.nodes[head]["district"] == graph.nodes[tail]["district"]:
        color = color_map[graph.nodes[tail]["district"]]
        plt.plot(x, y, c=color, linewidth=1)
    else:
        plt.plot(x, y, c="k", linewidth=1, linestyle="--")
    
# Iterate over each vertex, coloring them gray.
for vertex in tree.nodes():
    x, y = vertex[0], vertex[1]
    plt.plot(x, y, "ko", markersize=2, alpha=0.5)

plt.axis("off")
plt.savefig("./maps/grid.svg", format='svg', dpi=100000, orientation="landscape")
