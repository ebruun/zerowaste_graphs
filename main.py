from turtle import width
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import json


# ANALYSIS STRUCTURE (TURN ONE ON)
from data_in.simple import data_in
from graphs import Graph
from graph_plot import Plotter


def create_graph2():
    G = nx.DiGraph()

    G.add_nodes_from([1, 2, 3, 4])
    G.add_weighted_edges_from([(1, 2, 0.4), (2, 3, 0.2), (3, 1, 0.3)])

    G.add_edge(1, 4, color="r", weight=3)

    labels = ["yo"]
    nx.set_edge_attributes(G, labels, "labels")

    node_labels = ["sick"]
    nx.set_node_attributes(G, node_labels, "node_labels")

    return G


if __name__ == "__main__":

    G = create_graph2()
    a = nx.to_dict_of_dicts(G)
    print(a)

    f = "test_out.json"
    with open(f, "w") as outfile:
        json.dump(a, outfile, indent=4)

    f = "test_in.json"
    with open(f, "r") as infile:
        a = json.load(infile)

    G = nx.from_dict_of_dicts(a["edge"], create_using=nx.DiGraph)

    nx.set_node_attributes(G, a["node"])
    print(G)

    colors = nx.get_edge_attributes(G, "color").values()
    weights = nx.get_edge_attributes(G, "weight").values()
    n_colors = nx.get_node_attributes(G, "color").values()

    pos = nx.planar_layout(G)

    nx.draw(
        G,
        pos=pos,
        with_labels=True,
        edge_color=colors,
        node_color=n_colors,
        width=list(weights) * 5,
    )
    plt.show()
