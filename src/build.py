import copy
import networkx as nx

from src.algorithms import (
    check_fixed_nodes_support,
    check_fixed_nodes_cut,
    calc_multimemb_remove,
    calc_subg,
)

from src.io import read_json


def _add_nodes(G, node_data):
    G.add_nodes_from(node_data.keys())
    nx.set_node_attributes(G, node_data)


def _add_edges(G, edge_data):
    add_list = []
    for k, v in edge_data.items():
        for k2, v2 in v.items():
            add_list.append((k, k2, v2))

    G.add_edges_from(add_list)


def _add_in_extra_edge(G, K_joined):
    """
    Adds missing edges between K_joined and a subgraph H of the original graph G.

    Parameters:
    - G (networkx.Graph): Original graph.
    - K_joined (networkx.Graph): Joined subgraphs.

    Returns:
    None
    """
    H = G.subgraph(K_joined.nodes())

    edges_graph1 = set(H.edges())
    edges_graph2 = set(K_joined.edges())

    missing_edges = edges_graph1 - edges_graph2

    for n1, n2 in missing_edges:
        data = G.get_edge_data(n1, n2)
        K_joined.add_edges_from([(n1, n2, data[0])])
        K_joined.edges[n1, n2, 0]["color"] = "black"

    print("\nmissing edges in joined subgraphs: {}".format(missing_edges))


######################################################################


def bld_g_full(folder_in):
    print("\n\n##1. BUILD FULL SUPPORT HIERARCHY GRAPH##")
    G = nx.empty_graph(create_using=nx.MultiDiGraph())

    data_in_list = [
        "data_R.json",
        "data_W.json",
        "data_N.json",
        "data_E.json",
        "data_S.json",
    ]

    for f in data_in_list:
        edge_data, node_data = read_json(folder_in, f)

        _add_nodes(G, node_data)
        _add_edges(G, edge_data)

    return G


def bld_subg_single_remove(G, rm_membs):
    K_save = []
    n2check_save = []

    for rm_memb in rm_membs:
        print("\n\n##2A. BUILD SUBGRAPH FOR MEMBER REMOVAL: {}##".format(rm_memb))
        K = calc_subg(G.copy(), rm_memb)
        fxd_n_cut_rmv = check_fixed_nodes_cut(G, K)
        n2check = check_fixed_nodes_support(G, K, rm_memb, fxd_n_cut_rmv)

        K_save.append(K)
        n2check_save.extend(n2check)

    n2check_save = list(set(n2check_save))  # remove duplicates

    return K_save, n2check_save


def bld_subg_multi(G, Ks, rms, nodes_check_support):
    print("\n\n##3A. BUILD SUBGRAPH FOR MULTIPLE MEMBERS REMOVAL##")

    K_joined = nx.compose_all(Ks)
    _add_in_extra_edge(G, K_joined)

    K_joined = calc_multimemb_remove(G, K_joined, rms, nodes_check_support)

    return K_joined
