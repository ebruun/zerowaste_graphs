import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import pathlib

from algorithms import single_member_remove


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


def add_nodes(G, node_data):
    G.add_nodes_from(node_data.keys())
    nx.set_node_attributes(G, node_data)


def add_edges(G, edge_data):
    add_list = []
    for k, v in edge_data.items():
        for k2, v2 in v.items():
            add_list.append((k, k2, v2))

    G.add_edges_from(add_list)


def get_node_pos(G, scale=1):

    pos_fixed = {}
    for k, v in nx.get_node_attributes(G, "pos").items():
        pos_fixed[k] = tuple(t * scale for t in eval(v))

    return pos_fixed


def draw_graph(G, pos_fixed, filename, scale=1, plt_show=False):

    # f = plt.figure(1, figsize=(11, 8.5))
    f = plt.figure(1)

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
            G=G,
            pos=pos,
            node_size=s * scale,
            nodelist=[n[0]],
            node_color=n[1]["color"],
            node_shape=n_shape,
        )

        n_size.append(s * scale)  # for correct arrow location

    for e in G.edges(data=True):

        if "style" in e[2]:  # curved arrows
            c = e[2]["style"]
        else:
            c = "arc3, rad=0.0"

        if "edge_style" in e[2]:  # curved arrows
            s = e[2]["edge_style"]
        else:
            s = "solid"

        nx.draw_networkx_edges(
            G,
            pos,
            node_size=n_size,
            edgelist=[(e[0], e[1])],
            edge_color=e[2]["color"],
            width=e[2]["weight"],
            connectionstyle=c,
            style=s,
            arrows=True,
        )

    nx.draw_networkx_labels(
        G=G,
        pos=pos,
        font_size=6 * (scale * 0.7),
        font_color="white",
        font_weight="bold",
    )

    f = plt.gcf()
    f.tight_layout()
    plt.savefig(filename, dpi=600)

    if plt_show:
        plt.show()

    plt.close()


def build_full_graph(folder, filename, draw=False, show=False):

    G = nx.empty_graph(create_using=nx.MultiDiGraph())

    data_in_list = [
        "data_R.json",
        "data_W.json",
        "data_N.json",
        "data_E.json",
        "data_S.json",
    ]

    for f in data_in_list:

        edge_data, node_data = read_json(folder, f)

        add_nodes(G, node_data)
        add_edges(G, edge_data)

    if draw:
        draw_graph(
            G=G,
            pos_fixed=get_node_pos(G),
            filename="graphs_out/{}".format(filename),
            scale=1,
            plt_show=show,
        )

    return G


def build_member_subgraph(G, remove_members, draw=False, show=False):

    for m in remove_members:
        G_copy = G.copy()
        K = single_member_remove(G_copy, m)

        # Only do it if not START/END node
        if draw and K.number_of_nodes() > 1:
            draw_graph(
                G=K,
                pos_fixed=get_node_pos(K, scale=1),
                filename="graphs_out/{}.png".format(m),
                scale=1.5,
                plt_show=show,
            )

    return K


if __name__ == "__main__":

    G = build_full_graph(folder="data_in", filename="_full_structure.png", draw=True, show=False)

    # remove_members = ["WP1_6"]
    remove_members = G.nodes()

    K = build_member_subgraph(G=G, remove_members=remove_members, draw=True, show=False)
