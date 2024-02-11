import networkx as nx

from src.drawing import node_draw_settings

from src.algorithms import (
    calc_subg_multi,
    check_fixed_nodes_support,
    check_fixed_nodes_cut,
    calc_subg_single,
)

from src.algo_sequence import (
    find_n_active,
    select_n_active,
    set_rob_support,
    crnt_subg_save,
    crnt_subg_process,
    new_subg_relabel,
)

from src.io import (
    read_json,
    read_json_subgraph,
)


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


def _create_subg(G, data, i):
    data_nodes = data[str(i)]["nodes"]
    data_title = data[str(i)]["title"]

    subset_nodes = list(data_nodes)

    K = G.subgraph(subset_nodes)
    K.graph["step"] = i
    K.graph["title"] = "Step {}: {}".format(i, data_title)

    for key, value in data_nodes.items():
        node_draw_settings(K, [key], value)

    nx.set_edge_attributes(K, "black", "color")

    return K


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


def bld_g_sub(G, folder_in, steps):
    """
    From the full graph, generate a subgraph based on given subset (for phase 3 figures)
    """
    f = "_subgraphs.json"
    data = read_json_subgraph(folder_in, f)

    Ks = []

    for i in range(steps + 1):
        K = _create_subg(G.copy(), data, i)

        Ks.append(K)

    return Ks


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
    """
    Phase 1 and 2. Builds a disassembly sequence based on the provided graph and removal members.

    Parameters:
    - K (networkx.Graph): The input graph representing the assembly structure.
    - rm_membs (list): A list of nodes to be as active member targets.

    Returns:
    - tuple: A tuple containing two lists: `saved_K` - a list of saved graph states during the disassembly process,
      and `saved_seq` - a list representing the disassembly sequence.

    The function iteratively selects nodes to remove from the graph `K` based on the provided `rm_membs`
    and updates the disassembly sequence accordingly. It terminates when no more removal members can be
    selected from the current subgraph.

    During each step of the disassembly sequence, the following actions are performed:
    1. Identifies active nodes in the current subgraph.
    2. Allows the user to set new robotic supports if necessary.
    3. Selects a subset of active nodes for removal and robotic support addition.
    4. Saves the current state of the graph.
    5. Processes the current subgraph by removing selected elements.
    6. Relabels the graph for the next iteration.
    7. Prints the remaining nodes and the sequence so far.

    Note: The input graph `K` is modified during the execution of this function.
    """
    print("\nCALCULATING DISASSEMBLY SEQUENCE")

    K_reduced = K.copy()
    saved_K, saved_seq = [], []
    step = 0

    while True:
        step += 1
        print(f"\nSTEP #{step}")

        # check if any start node in current subgraph
        n_active = find_n_active(K_reduced, n_type=["start", "robsupport_fixed"])

        # user set any new rob supports at start
        n_new_robsupport = set_rob_support(K_reduced)

        if not set(n_active).union(set(n_new_robsupport)):
            print("-Terminate: No more removal members")
            break

        # user select a subset for remove and rob support
        n_rmv_step, n_robfxd_step = select_n_active(K_reduced, n_active, n_new_robsupport)

        # save the current state
        crnt_subg_save(K_reduced, step, n_rmv_step, n_robfxd_step, saved_K, saved_seq)

        # PREPARE NEXT ITERATION
        # remove elements and update target member list
        crnt_subg_process(K_reduced, n_rmv_step, rm_membs)

        # relabel for new graph
        new_subg_relabel(K_reduced, rm_membs)

        # print output
        print("\n-remaining nodes are {}".format(K_reduced.nodes()))
        print("-sequence so far is {}".format(saved_seq))

    return saved_K, saved_seq
