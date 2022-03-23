from turtle import width
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import json


# ANALYSIS STRUCTURE (TURN ONE ON)
from data_in.simple import data_in


def create_graph2():
    G = nx.DiGraph()

    G.add_nodes_from([1, 2, 3, 4])
    G.add_weighted_edges_from([(1, 2, 0.4), (2, 3, 0.2), (3, 1, 0.3)])

    G.add_edge(1, 4, color="r", weight=3)

    labels = ["yo"]
    nx.set_edge_attributes(G, labels, "labels")

    node_labels = ["sick"]
    nx.set_node_attributes(G, node_labels, "node_labels")

    a = nx.to_dict_of_dicts(G)
    print(a)

    f = "test_out.json"
    with open(f, "w") as outfile:
        json.dump(a, outfile, indent=4)


def draw_graph(G, pos_fixed):

    colors = nx.get_edge_attributes(G, "color").values()
    weights = nx.get_edge_attributes(G, "weight").values()
    n_colors = nx.get_node_attributes(G, "color").values()

    pos = nx.spring_layout(G, pos=pos_fixed, fixed=pos_fixed.keys())

    nx.draw(
        G,
        pos=pos,
        with_labels=True,
        edge_color=colors,
        node_color=n_colors,
        width=list(weights),
    )
    plt.show()


if __name__ == "__main__":

    f = "test_in.json"
    with open(f, "r") as infile:
        a = json.load(infile)

    G = nx.from_dict_of_dicts(a["edge"], create_using=nx.DiGraph)
    nx.set_node_attributes(G, a["node"])

    f = "test_in2.json"
    with open(f, "r") as infile:
        a = json.load(infile)

    G.add_nodes_from(a["node"].keys())
    nx.set_node_attributes(G, a["node"])

    add_list = []
    for k, v in a["edge"].items():
        for k2, v2 in v.items():
            add_list.append((k, k2, v2))

    G.add_edges_from(add_list)

    pos_fixed = {}
    for k, v in a["node"].items():
        for k2, v2 in v.items():
            if k2 == "pos":
                pos_fixed[k] = eval(v2)

    pos_fixed = {}
    for k, v in nx.get_node_attributes(G, "pos").items():
        pos_fixed[k] = eval(v)

    print(pos_fixed)
    print(pos_fixed.keys())

    draw_graph(G, pos_fixed)
