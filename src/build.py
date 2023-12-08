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


def _add_in_extra_edge(G, K_combo, Ks):
    """
    when joining subgraphs,
    there might be a new edge necessary between nodes in diff subgraphs

    not super efficient since checking against itself in first loop
    """

    # first subgraph
    for K in Ks:
        for n1 in K.nodes():
            # second subgraph
            for M in Ks:
                for n2 in M.nodes():
                    # if in original but not in combo
                    if G.has_edge(n1, n2) and not K_combo.has_edge(n1, n2):
                        print("missing")
                        data = G.get_edge_data(n1, n2)
                        print(data)

                        K_combo.add_edges_from([(n1, n2, data[0])])
                        K_combo.edges[n1, n2, 0]["color"] = "black"


######################################################################


def bld_g_full(folder_in):
    print("\n1. BUILD FULL SUPPORT HIERARCHY GRAPH")
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
        print("\nSTEP 2A. BUILD SUBGRAPH FOR MEMBER REMOVAL: {}".format(rm_memb))
        K = calc_subg(G.copy(), rm_memb)
        fxd_n_cut_rmv = check_fixed_nodes_cut(G, K)
        n2check = check_fixed_nodes_support(G, K, rm_memb, fxd_n_cut_rmv)

        K_save.append(K)
        n2check_save.extend(n2check)

    n2check_save = list(set(n2check_save))  # remove duplicates

    return K_save, n2check_save


def bld_subg_multi(G, Ks, rms, nodes_check_support):
    print("\nSTEP 1. BUILD SUBGRAPH FOR MULTIPLE MEMBERS REMOVAL: {}".format(rms))

    Ks_copy = copy.deepcopy(Ks)
    K_joined = Ks_copy.pop(0)  # initialize one sub-graph to join rest too

    for K in Ks_copy:
        K_joined = nx.compose(K, K_joined)

    _add_in_extra_edge(G, K_joined, Ks)  # some edges might be missing between subgraphs

    K_joined = calc_multimemb_remove(G, K_joined, rms, nodes_check_support)

    return K_joined
