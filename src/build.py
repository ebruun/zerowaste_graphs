import networkx as nx

from src.algorithms import single_member_remove
from src.drawing import draw_graph
from src.io import read_json


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


def build_full_graph(folder, filename, scale=1, draw=False, show=False):

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
            pos_fixed=get_node_pos(G, scale),
            filename="graphs_out/{}".format(filename),
            scale=scale,
            plt_show=show,
        )

    return G


def build_member_subgraph(G, remove_members, scale, draw=False, show=False):

    for m in remove_members:
        G_copy = G.copy()
        K = single_member_remove(G_copy, m)

        # Only do it if not START/END node
        if draw and K.number_of_nodes() > 1:
            draw_graph(
                G=K,
                pos_fixed=get_node_pos(K, scale),
                filename="graphs_out/{}.png".format(m),
                scale=scale,
                plt_show=show,
            )

    return K
