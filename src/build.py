import networkx as nx

from src.algorithms import (
    calc_subg_multi,
    check_fixed_nodes_support,
    check_fixed_nodes_cut,
    calc_subg_single,
)

from src.algo_sequence import (
    calc_nodes_to_process,
    remove_disconnected_graphs,
    update_rm_list,
    relabel_graph,
    relabel_graph_ending,
    relabel_graph_fixed,
    make_graph_title,
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


def _user_input_parse(node_remove_step, num_agents):
    num_nodes_to_remove = len(node_remove_step)

    if num_nodes_to_remove > num_agents:
        user_input = input("which of these: {} ".format(node_remove_step))
        input_list_str = user_input.split()

        try:
            # Convert each string element to an integer
            input_list_int = [int(x) for x in input_list_str]

            print("\nParsed list of integers:", input_list_int)
        except ValueError:
            print("Invalid input. Please enter a valid list of integers.")

    elif num_nodes_to_remove == num_agents:
        input_list_int = list(range(0, num_agents))
    else:
        input_list_int = list(range(0, num_nodes_to_remove))

    input_list_int.sort(reverse=True)  # avoid index shift when remove

    return input_list_int


######################################################################


def bld_g_full(folder_in):
    """
    Build a full support hierarchy graph by reading edge and node data from JSON files.

    Parameters:
    - folder_in (str): The path to the folder containing JSON files.

    Returns:
    - networkx.MultiDiGraph: The constructed support hierarchy graph.

    Steps:
    1. Initialize an empty directed multigraph.
    2. Read edge and node data from specified JSON files.
    3. Add nodes and edges to the graph.
    4. Return the constructed support hierarchy graph.
    """
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
    """
    Build subgraphs for individual member removals and perform analysis.

    Parameters:
    - G (networkx.MultiDiGraph): The original support hierarchy graph.
    - rm_membs (list): List of members to be individually removed.

    Returns:
    - list: List of subgraphs corresponding to each member removal.

    Steps:
    1. Initialize an empty list to store subgraphs.
    2. For each member in the list to be removed:
    3. Build a subgraph corresponding to the member removal.
    4. Check for fixed nodes that need to be cut in the subgraph.
    5. Perform additional analysis on fixed nodes and their support in the original graph.
    6. Append the subgraph to the list.
    7. Return the list of subgraphs.

    """
    Ks = []

    for rm_memb in rm_membs:
        print("\n\n##2. BUILD SUBGRAPH FOR MEMBER REMOVAL: {}##".format(rm_memb))

        # Build a subgraph for the current member removal
        K = calc_subg_single(G.copy(), rm_memb)

        # Check for fixed nodes that need to be cut in the subgraph
        fxd_n_cut_rmv = check_fixed_nodes_cut(G, K)

        # Perform additional analysis on fixed nodes and their support in the original graph
        check_fixed_nodes_support(G, K, rm_memb, fxd_n_cut_rmv)

        # Append the subgraph to the list
        Ks.append(K)

    return Ks


def bld_subg_multi_remove(G, Ks, rm_membs):
    """
    Build a subgraph for multiple members removal and perform analysis.

    Parameters:
    - G (networkx.MultiDiGraph): The original support hierarchy graph.
    - Ks (list): List of subgraphs corresponding to individual member removals.
    - rm_membs (list): List of members to be removed.

    Returns:
    - networkx.MultiDiGraph: A subgraph representing the removal of multiple members.

    Steps:
    1. Compose all individual subgraphs into a single subgraph.
    2. Add any missing edges between nodes in the composed subgraph and the original graph.
    3. Check for fixed nodes that need to be cut in the composed subgraph.
    4. Perform additional analysis on fixed nodes and their support in the original graph.
    5. Return the composed subgraph.
    """
    print("\n\n##3. BUILD SUBGRAPH FOR MULTIPLE MEMBERS REMOVAL##")

    # Compose all individual subgraphs into a single subgraph
    K_joined = calc_subg_multi(Ks)

    # Add any missing edges between nodes in the composed subgraph and the original graph
    _add_in_extra_edge(G, K_joined)

    # Check for fixed nodes that need to be cut in the composed subgraph
    fxd_n_cut_rmv = check_fixed_nodes_cut(G, K_joined)

    # Perform additional analysis on fixed nodes and their support in the original graph
    check_fixed_nodes_support(G, K_joined, rm_membs, fxd_n_cut_rmv)

    return K_joined


def bld_sequence(K, rm_membs):
    print("\nCALCULATING DISASSEMBLY SEQUENCE")

    K_reduced = K.copy()
    K_reduced_list = []
    sequence = []

    num_agents = 2
    steps = 0

    while True:
        print("\nSTART LOOP")

        # check for any start nodes
        nodes_to_remove = calc_nodes_to_process(K_reduced, "start", num_agents)

        if not nodes_to_remove:
            print("No more removal members, terminate...")
            break

        # save the current subgraph and sequence infomation
        while nodes_to_remove:
            steps += 1
            user_input = _user_input_parse(nodes_to_remove, num_agents)

            node_remove_step = [nodes_to_remove.pop(index) for index in user_input]

            print(f"Processing nodes in step {steps}: {node_remove_step}")
            sequence.append(node_remove_step)
            K_reduced.graph["title"] = make_graph_title(steps, node_remove_step)
            K_reduced_list.append(K_reduced.copy())

            # process the current subgraph and prep for next loop
            K_reduced.remove_nodes_from(node_remove_step)
            rm_membs = update_rm_list(node_remove_step, rm_membs)
            # remove_disconnected_graphs(K_reduced)

        # relabel remaining graph
        relabel_graph(K_reduced, rm_membs)
        relabel_graph_ending(K_reduced)
        relabel_graph_fixed(K_reduced)

        # print output
        print("remaining nodes are {}".format(K_reduced.nodes()))
        print("sequence so far is {}".format(sequence))

    return K_reduced_list, sequence
