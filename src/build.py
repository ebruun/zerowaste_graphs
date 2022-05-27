import networkx as nx

from src.algorithms import check_connected, check_cut, single_member_remove
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

    scale = [scale, scale * 2]

    pos_fixed = {}
    for k, v in nx.get_node_attributes(G, "pos").items():
        pos_fixed[k] = tuple(dim * s for dim, s in zip(eval(v), scale))

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
        K, n = single_member_remove(G_copy, m)

        # Only draw it if not START/END node (since pointless)
        if draw and K.number_of_nodes() > 1:
            draw_graph(
                G=K,
                pos_fixed=get_node_pos(K, scale),
                filename="graphs_out/{}.png".format(m),
                scale=scale,
                plt_show=show,
            )

    return K, n


def _add_in_extra_edge(G, K_combo, K1, K2):
    """
    when joining two subgraphs,
    there might be a new edge necessary between nodes in diff subgraphs
    """

    for n1 in K1.nodes():
        for n2 in K2.nodes():
            # if G.has_edge(n1,n2) and not K_combo.has_edge(n1,n2):
            if G.has_edge(n1, n2) and not K_combo.has_edge(n1, n2):
                print("missing")
                data = G.get_edge_data(n1, n2)
                print(data)

                K_combo.add_edges_from([(n1, n2, data[0])])
                K_combo.edges[n1, n2, 0]["color"] = "black"


def build_joined_subgraph(
    G, K1, K2, remove_members, nodes_check_support, name, scale, draw=False, show=False
):

    print("\n\nJOINED SUBGRAPH CHECKS")

    K_combo = nx.compose(K2, K1)
    _add_in_extra_edge(G, K_combo, K1, K2)

    print("-- NODES check support: {}".format(nodes_check_support))

    nodes_cut, nodes_fully_removed = check_cut(G, K_combo)

    nodes_fully_removed.extend(remove_members)
    nodes_fully_removed = list(set(nodes_fully_removed))  # remove duplicates

    nodes_check_support.extend(nodes_cut)
    nodes_check_support = list(set(nodes_check_support))
    nodes_check_support = list(set(nodes_check_support) - set(nodes_fully_removed))

    print("-- NODES fully removed: {}".format(nodes_fully_removed))
    print("-- NODES to check support on: {}".format(nodes_check_support))

    _ = check_connected(G, K_combo, nodes_fully_removed, nodes_check_support)

    if draw:
        draw_graph(
            G=K_combo,
            pos_fixed=get_node_pos(K_combo),
            filename="graphs_out/_{}".format(name),
            scale=scale,
            plt_show=show,
        )
