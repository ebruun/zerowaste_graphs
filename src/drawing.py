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
        "remove": {"node_type": "remove", "color": "tab:red", "size": 600, "node_shape": "8"},
        "start": {"node_type": "start", "color": "tab:green", "size": 400, "node_shape": "o"},
        "normal": {"node_type": "normal", "color": "tab:grey", "size": 400, "node_shape": "o"},
        "remove_start": {
            "node_type": "remove_start",
            "color": "tab:red",
            "size": 600,
            "node_shape": "8",
        },
        "end_foundation": {
            "node_type": "end_foundation",
            "color": "black",
            "size": 600,
            "node_shape": "8",
        },
        "end_2sides_fixed": {
            "node_type": "end_2sides_fixed",
            "color": "black",
            "size": 600,
            "node_shape": "h",
        },
        "end_1sides_fixed": {
            "node_type": "end_1sides_fixed",
            "color": "black",
            "size": 450,
            "node_shape": "s",
        },
        "danger_1side_fixed": {
            "node_type": "danger_1side_fixed",
            "color": "tab:orange",
            "size": 450,
            "node_shape": "s",
        },
        "normal_1side_fixed": {
            "node_type": "normal_1side_fixed",
            "color": "tab:grey",
            "size": 400,
            "node_shape": "o",
        },
        "robsupport_fixed": {
            "node_type": "robsupport_fixed",
            "color": "tab:pink",
            "size": 400,
            "node_shape": "s",
        },
    }

    # make into a list if a single variable
    if not isinstance(nodes, list):
        nodes = [nodes]

    for n in nodes:
        attributes = attribute_mapping.get(node_type, {})
        G.nodes[n].update(attributes)


def draw_graph(G, filepath, scale=1, plt_show=False, plt_save=False, plt_text=False):
    pos_fixed = _get_node_pos(G, scale)  # get location to draw

    if scale == 1:
        f = plt.figure(1, figsize=(11, 8.5))
    else:
        f = plt.figure(1)

    pos = nx.spring_layout(G, pos=pos_fixed, fixed=pos_fixed.keys())

    n_size = []  # for drawing arrows correct location
    for n, data in G.nodes(data=True):
        # 2nd value is the default
        s = data.get("size", 500)
        n_shape = data.get("node_shape", "o")
        color = data.get("color", "black")

        nx.draw_networkx_nodes(
            G=G,
            pos=pos,
            node_size=s * scale,
            nodelist=[n],
            node_color=color,
            node_shape=n_shape,
        )

        n_size.append(s * scale)  # for correct arrow location

    for u, v, data in G.edges(data=True):
        # 2nd value is the default
        c = data.get("style", "arc3, rad=0.0")
        s = data.get("edge_style", "solid")
        color = data.get("color", "black")
        weight = data.get("weight", 1.0)

        nx.draw_networkx_edges(
            G,
            pos,
            node_size=n_size,
            edgelist=[(u, v)],
            edge_color=color,
            width=weight,
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

    # to give a bit of vertical padding
    plt.text(
        x=0.15,
        y=1.08,
        s=" ",
        fontsize=18,
        fontweight="bold",
        ha="left",
        va="center",
        transform=plt.gca().transAxes,
    )

    if plt_text:
        plt.text(
            x=0.04,
            y=1.07,
            s=G.graph["title"],
            fontsize=16,
            fontweight="bold",
            ha="left",
            va="center",
            bbox=dict(facecolor="white", edgecolor="red", boxstyle="round,pad=0.5"),
            transform=plt.gca().transAxes,
        )

    f.tight_layout()
    plt.axis("off")  # no border around fig

    if plt_save:
        plt.savefig(filepath, dpi=600)

    if plt_show:
        plt.show()

    plt.close()
