from tkinter import E
from turtle import width
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import pathlib


# ANALYSIS STRUCTURE (TURN ONE ON)
from data_in.simple import data_in


def _create_file_path(folder, filename):
    """create output data path.

    Returns:
        path: Output data path

    """
    path = pathlib.PurePath(
        pathlib.Path.cwd(),
        folder,
        filename,
    )

    # print("created path...", path)
    return path


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


def move_figure(f, x, y):
    """Move figure's upper left corner to pixel (x, y)"""
    backend = mpl.get_backend()
    if backend == "TkAgg":
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == "WXAgg":
        f.canvas.manager.window.SetPosition((x, y))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(x, y)


def draw_graph(G, pos_fixed):

    n_colors = nx.get_node_attributes(G, "color").values()

    pos = nx.spring_layout(G, pos=pos_fixed, fixed=pos_fixed.keys())

    f = plt.figure(1, figsize=(16, 10))
    f.tight_layout()

    for e in G.edges(data=True):

        if "style" in e[2]:
            c = e[2]["style"]
        else:
            c = "arc3, rad=0.0"

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(e[0], e[1])],
            edge_color=e[2]["color"],
            width=e[2]["weight"],
            connectionstyle=c,
        )

    ax = plt.gca()
    print(ax)
    # ax.set_aspect('equal')

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=n_colors,
        node_size=300,
    )

    nx.draw_networkx_labels(G, pos, font_size=7, font_color="white")

    ax = plt.gca()
    f = plt.gcf()

    plt.show()
    # plt.savefig("full_structure.png", dpi=300)


def read_json(folder, name):

    p = _create_file_path(folder, name)

    with open(p, "r") as infile:
        a = json.load(infile)

    edges = a["edge"]
    nodes = a["node"]

    return edges, nodes


def add_nodes(G, node_data):
    G.add_nodes_from(node_data.keys())
    nx.set_node_attributes(G, node_data)


def add_edges(G, edge_data):
    add_list = []
    for k, v in edge_data.items():
        for k2, v2 in v.items():
            add_list.append((k, k2, v2))

    G.add_edges_from(add_list)


def get_node_pos(G):

    pos_fixed = {}
    for k, v in nx.get_node_attributes(G, "pos").items():
        pos_fixed[k] = eval(v)

    return pos_fixed


if __name__ == "__main__":

    _create_file_path("test", "test2")

    G = nx.empty_graph(create_using=nx.DiGraph())

    data_in_list = [
        "data_roof.json",
        "data_wall_L.json",
        "data_wall_T.json",
        "data_wall_R.json",
        "data_wall_B.json",
    ]

    for f in data_in_list:

        edge_data, node_data = read_json("data_in", f)

        add_nodes(G, node_data)
        add_edges(G, edge_data)

    draw_graph(G, get_node_pos(G))
