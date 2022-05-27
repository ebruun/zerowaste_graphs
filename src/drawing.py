import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl


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


def draw_graph(G, pos_fixed, filename, scale=1, plt_show=False):

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
        font_size=6 * (scale * 0.8),
        font_color="white",
        font_weight="bold",
    )

    f = plt.gcf()
    f.tight_layout()
    plt.axis("off")  # no border around fig
    plt.savefig(filename, dpi=600)

    if plt_show:
        plt.show()

    plt.close()
