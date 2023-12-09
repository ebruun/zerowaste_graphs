import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl


def _get_node_pos(G, scale=1):
    scale = [scale, scale * 2]

    pos_fixed = {}
    for k, v in nx.get_node_attributes(G, "pos").items():
        pos_fixed[k] = tuple(dim * s for dim, s in zip(eval(v), scale))

    return pos_fixed


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


def edge_draw_settings(G, edges, type):
    for e in edges:
        if type == "cut":
            G.edges[e[0], e[1], 0]["edge_style"] = "dashed"
            G.edges[e[0], e[1], 0]["weight"] = 1.5
            G.edges[e[0], e[1], 0]["color"] = "tab:red"

            G.edges[e[1], e[0], 0]["edge_style"] = "dashed"
            G.edges[e[1], e[0], 0]["weight"] = 1.5
            G.edges[e[1], e[0], 0]["color"] = "tab:red"


def node_draw_settings(G, nodes, node_type):
    attribute_mapping = {
        "remove": {"color": "tab:red", "size": 600, "node_shape": "8"},
        "remove_start": {"color": "tab:red", "size": 600, "node_shape": "8"},
        "end_foundation": {"color": "black", "size": 600, "node_shape": "8"},
        "end_2sides_fixed": {"color": "black", "size": 600, "node_shape": "h"},
        "end_1sides_fixed": {"color": "black", "size": 450, "node_shape": "s"},
        "danger_1side_fixed": {"color": "orange", "size": 450, "node_shape": "s"},
        "normal": {"color": "tab:grey", "size": 400},
        "normal_1side_fixed": {"color": "tab:grey", "size": 400},
        "start": {"color": "tab:green", "size": 400},
    }

    for n in nodes:
        attributes = attribute_mapping.get(node_type, {})
        G.nodes[n].update(attributes)

    # for n in nodes:
    #     if node_type == "remove":
    #         G.nodes[n]["color"] = "tab:red"
    #         G.nodes[n]["size"] = 600
    #         G.nodes[n]["node_shape"] = "8"
    #     elif node_type == "remove_start":
    #         G.nodes[n]["color"] = "tab:red"
    #         G.nodes[n]["size"] = 600
    #         G.nodes[n]["node_shape"] = "8"
    #     elif node_type == "end_foundation":
    #         G.nodes[n]["color"] = "black"
    #         G.nodes[n]["size"] = 600
    #         G.nodes[n]["node_shape"] = "8"
    #     elif node_type == "end_2sides_fixed":
    #         G.nodes[n]["color"] = "black"
    #         G.nodes[n]["size"] = 600
    #         G.nodes[n]["node_shape"] = "h"
    #     elif node_type == "end_1sides_fixed":
    #         G.nodes[n]["color"] = "black"
    #         G.nodes[n]["size"] = 450
    #         G.nodes[n]["node_shape"] = "s"
    #     elif node_type == "danger_1side_fixed":
    #         G.nodes[n]["color"] = "orange"
    #         G.nodes[n]["size"] = 450
    #         G.nodes[n]["node_shape"] = "s"
    #     elif node_type == "normal":
    #         G.nodes[n]["color"] = "tab:grey"
    #         G.nodes[n]["size"] = 400
    #     elif node_type == "normal_1side_fixed":
    #         G.nodes[n]["color"] = "tab:grey"
    #         G.nodes[n]["size"] = 400
    #     elif node_type == "start":
    #         G.nodes[n]["color"] = "tab:green"
    #         G.nodes[n]["size"] = 400


def draw_graph(G, filepath, scale=1, plt_show=False, plt_save=False):
    pos_fixed = _get_node_pos(G, scale)  # get location to draw

    if scale == 1:
        f = plt.figure(1, figsize=(11, 8.5))
    else:
        f = plt.figure(1)

    pos = nx.spring_layout(G, pos=pos_fixed, fixed=pos_fixed.keys())

    n_size = []  # for drawing arrows correct location
    for n in G.nodes(data=True):
        if "size" in n[1]:
            s = n[1]["size"]
        else:
            s = 500

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
        font_size=6 * (scale * 0.8),
        font_color="white",
        font_weight="bold",
    )

    f = plt.gcf()
    f.tight_layout()
    plt.axis("off")  # no border around fig

    if plt_save:
        plt.savefig(filepath, dpi=600)

    if plt_show:
        plt.show()

    plt.close()
