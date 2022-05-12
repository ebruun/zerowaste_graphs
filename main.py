import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import pathlib

from algorithms import phase_1


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

    print("created path...", path)
    return path


def read_json(folder, name):

    p = _create_file_path(folder, name)

    with open(p, "r") as infile:
        a = json.load(infile)

    edges = a["edge"]
    nodes = a["node"]

    return edges, nodes


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


def draw_graph(G, pos_fixed, name):

    f = plt.figure(1, figsize=(11, 8.5))

    pos = nx.spring_layout(G, pos=pos_fixed, fixed=pos_fixed.keys())

    n_size = []  # for drawing arrows correct location
    for n in G.nodes(data=True):

        if "size" in n[1]:
            s = n[1]["size"]
        else:
            s = 300

        if "node_shape" in n[1]:
            n_shape = n[1]["node_shape"]
        else:
            n_shape = "o"

        nx.draw_networkx_nodes(
            G,
            pos=pos,
            node_size=s,
            nodelist=[n[0]],
            node_color=n[1]["color"],
            node_shape=n_shape
        )

        n_size.append(s)

    for e in G.edges(data=True):

        if "style" in e[2]:  # curved arrows
            c = e[2]["style"]
        else:
            c = "arc3, rad=0.0"

        nx.draw_networkx_edges(
            G,
            pos,
            node_size=n_size,
            edgelist=[(e[0], e[1])],
            edge_color=e[2]["color"],
            width=e[2]["weight"],
            connectionstyle=c,
            arrows=True,
        )

    nx.draw_networkx_labels(G, pos, font_size=6, font_color="white")

    f = plt.gcf()
    f.tight_layout()
    plt.savefig(name, dpi=300)
    plt.show()


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

    G = nx.empty_graph(create_using=nx.MultiDiGraph())

    data_in_list = [
        "data_roof_copy.json",
        "data_wall_L_copy.json",
        "data_wall_T_copy.json",
        "data_wall_R_copy.json",
        "data_wall_B_copy.json",
    ]

    for f in data_in_list:

        edge_data, node_data = read_json("data_in", f)

        add_nodes(G, node_data)
        add_edges(G, edge_data)

    # draw_graph(G, get_node_pos(G), "full_structure.png")

    remove_member = "P6_L"
    K = phase_1(G, remove_member)
    # draw_graph(K, get_node_pos(K), "partial_{}.png".format(remove_member))
    draw_graph(K, get_node_pos(K), "partial_.png")
