import networkx as nx
from src.drawing import node_draw_settings, edge_draw_settings


def _check_if_fixed_exists_multi(G, node, nodes_to_check):
    """
    Check if the node has fixed connections with any node in the list in both directions.

    Parameters:
    - G (networkx.Graph): The graph.
    - node: The node to check.
    - nodes_to_check (list): List of nodes to check against.

    Returns:
    - True if the node has fixed connections with any node in the list in both directions, False otherwise.
    """
    return any(G.has_edge(node, n) and G.has_edge(n, node) for n in nodes_to_check)


def _check_if_fixed_exists(G, node1, node2):
    """
    Check if node1 is connected with node2 in both directions.

    Parameters:
    - G (networkx.Graph): The graph.
    - node1: The first node.
    - node2: The second node.

    Returns:
    - True if node1 has fixed connections with node2 in both directions, False otherwise.
    """
    return G.has_edge(node1, node2) and G.has_edge(node2, node1)


def _count_fixed_sides(G, n):
    """
    Check on how many sides node is fixed.

    Parameters:
    - G (networkx.Graph): The graph.
    - n: The target node.

    Returns:
    - The count of fixed sides and a list of fixed edges as tuples.
    """

    fixed_e_count = 0
    e_fixed = []

    neighbors = list(G.neighbors(n))

    for neighbor in neighbors:
        if _check_if_fixed_exists(G, n, neighbor):
            fixed_e_count += 1
            e_fixed.append((n, neighbor))  # save as tuple ('n1','n2')

    return fixed_e_count, e_fixed


def _find_adjacent_nodes(G, n, n_queue, n_saved):
    """
    Find adjacent nodes to a given node in a directed graph.

    Parameters:
    - G (networkx.DiGraph): The directed graph.
    - n: The target node.
    - n_queue (list): The queue of nodes to check.
    - n_saved (list): The list of nodes already visited.

    Returns:
    - Updated node queue and list of visited nodes.
    """

    successors = list(G.successors(n))
    predecessors = list(G.predecessors(n))

    adjacent_nodes = successors + predecessors

    # don't add already visited or already in queue
    n_queue.extend(set(adjacent_nodes) - set(n_saved).union(set(n_queue)))

    return n_queue, n_saved


def _check_node_type(G, n_check, rm_membs):
    """
    Determine the type of a graph node based on specified conditions.

    Parameters:
    - G (networkx.Graph): The graph.
    - n_check: The node to be evaluated.
    - rm_membs: A single node or a list of nodes to be removed.

    Returns:
    - str: A string representing the type of the node, such as "remove_start", "remove", "start",
      "end_foundation", "end_2sides_fixed", "danger_1side_fixed", "normal_1side_fixed", or "normal".
    """
    print("\nCHECKING NODE TYPE OF: {}".format(n_check))

    if not isinstance(rm_membs, list):
        rm_membs = [rm_membs]

    in_degree = G.in_degree(n_check)
    out_degree = G.out_degree(n_check)
    fixed_sides_count, _ = _count_fixed_sides(G, n_check)

    if n_check in rm_membs and in_degree == 0:
        # don't add to queue if remove is also start node
        print("--REMOVE & START NODE")
        node_type = "remove_start"
    elif n_check in rm_membs:
        print("--REMOVE NODE")
        node_type = "remove"
    elif in_degree == 0:
        print("--START NODE, in_degree=0")
        node_type = "start"
    elif out_degree == 0:
        print("--END NODE, out_degree=0")
        node_type = "end_foundation"
    elif fixed_sides_count == 2:
        print("--END NODE, fixed on TWO sides")
        node_type = "end_2sides_fixed"
    elif fixed_sides_count == 1:
        if _check_if_fixed_exists_multi(G, n_check, rm_membs):
            print("-- DANGER NODE, fixed on ONE side, the fixed connection is to removal member")
            node_type = "danger_1side_fixed"
        elif not any(G.has_edge(n_check, m) for m in rm_membs):
            print("-- DANGER NODE, fixed on ONE side, connected somewhere in structure")
            node_type = "danger_1side_fixed"
        else:
            print("-- NORMAL REMOVE NODE, fixed on ONE side, normal connection to member to remove")
            node_type = "normal_1side_fixed"
    else:
        print("-- NORMAL NODE")
        node_type = "normal"

    return node_type


def _check_connected(G, K, fxd_n_cut_rmv, fxd_n_check):
    """
    Check if fixed members have at least TWO other support connections after the removal of the member.
    If it is fixed (not being cut) then it just needs 1 additional connection for a total of 2 to be safe
    If it has enough edges then it is considered fixed support in this disassembly step

    Parameters:
    - G (networkx.Graph): The overall graph.
    - K (networkx.Graph): The subgraph for member removal.
    - fxd_n_cut_rmv (list): List of fully removed fixed nodes.
    - fxd_n_check (list): List of fixed nodes to check.

    Returns:
    - tuple: Lists of nodes with safe support for 1-side fixed, 2-side fixed, and unsafe support.

    """

    print("\nCHECKING IF NODES {} HAVE ENOUGH SUPPORT".format(fxd_n_check))

    n_safe_fix1 = []
    n_safe_fix2 = []
    n_notsafe = []

    for n in fxd_n_check:
        print("\nCHECK FIXED NODE {}".format(n))

        e_G = list(G.out_edges(n))  # member supported by (START)
        e_K = list(K.out_edges(n))  # supporting members to be removed

        num_supports = len(e_G) - len(e_K)
        print("-- {} supports left. These members being removed: {}".format(num_supports, e_K))

        flag = False
        # if fixed edge is not being cut, add back
        for e in e_K:
            if _check_if_fixed_exists(G, e[0], e[1]):
                if e[0] not in fxd_n_cut_rmv and e[1] not in fxd_n_cut_rmv:
                    print("-- fixed not cut, ADD support back in")
                    flag = True
                    num_supports += 1
                else:
                    print("-- fixed is cut, DO NOT ADD support back in")

        # distinguish between 2-support and 1-support
        if num_supports < 2:
            print("-- DANGER, only {} SUPPORTS".format(num_supports))
            n_notsafe.append(n)
        else:
            print("-- SAFE, w/ {} SUPPORTS".format(num_supports))
            if _count_fixed_sides(G, n)[0] == 2:
                if flag:
                    n_safe_fix2.append(n)
                else:
                    n_safe_fix1.append(n)
            elif _count_fixed_sides(G, n)[0] == 1:
                n_safe_fix1.append(n)

    return n_safe_fix1, n_safe_fix2, n_notsafe


##############################################################################


def calc_subg_single(G, rm_memb):
    """
    STEP A. Calculate a subgraph based on a single member set for removal.

    Parameters:
    - G (networkx.MultiDiGraph): The original support hierarchy graph.
    - rm_memb: The member set for removal.

    Returns:
    - networkx.MultiDiGraph: The calculated subgraph.

    Steps:
    1. Initialize a queue with the member set for removal.
    2. Initialize an empty set for checked nodes.
    3. Loop through the queue and add adjacent nodes based on node types.
    4. Build a subgraph from the checked nodes.
    5. Set edge attributes for visualization.

    """

    nodes_queue = [rm_memb]  # queue to check
    nodes_checked = []  # saved list of checked nodes

    # A. Loop through nodes queue, and see if their adjacents should be added
    while nodes_queue:
        n_check = nodes_queue.pop(0)
        node_type = _check_node_type(G, n_check, rm_memb)

        if node_type in ["remove", "normal", "normal_1side_fixed"]:
            nodes_queue, nodes_checked = _find_adjacent_nodes(
                G, n_check, nodes_queue, nodes_checked
            )

        nodes_checked.append(n_check)
        node_draw_settings(G, [n_check], node_type)

        print("current n_queue: ", nodes_queue)
        print("current n_checked: ", nodes_checked)

    print("\nNODES IN FINAL SUBGRAPH:", nodes_checked)

    K = G.subgraph(nodes_checked)  # sub-graph built from checked nodes
    nx.set_edge_attributes(K, "black", "color")

    return K


def calc_subg_multi(Ks):
    """
    STEP A: Combine multiple subgraphs for single member removals into a single graph.

    Parameters:
    - Ks (list): List of subgraphs to be combined.

    Returns:
    - networkx.Graph: The graph resulting from the composition of all subgraphs.

    """
    return nx.compose_all(Ks)


def check_fixed_nodes_cut(G, K):
    """
    STEP B. Identify nodes in a subgraph that are fully removed and have fixed connections.
    For such nodes, mark the fixed connections as cut and return the nodes that are fully removed.

    Parameters:
    - G (networkx.Graph): The original graph.
    - K (networkx.Graph): The subgraph to analyze.

    Returns:
    - list: Nodes in the subgraph that have fixed connections cut and are fully removed.

    Steps:
    1. Check if a member in the subgraph is fully removed by comparing in and out degrees.
    2. For fully removed members, identify fixed connections (edges with the same node in both in-edges and out-edges).
    3. Mark these fixed connections as cut and add the nodes to the result sets.
    4. Return the nodes that are partially or fully removed with fixed connections cut

    """

    print("\n\n2B. CHECK WHAT FIXED EDGES NEED TO BE CUT")

    fxd_n_cut = set()
    fxd_n_cut_rmv = set()

    for n in K.nodes():
        print("\nchecking node {}".format(n))

        fully_removed = (K.in_degree(n) + K.out_degree(n)) == (G.in_degree(n) + G.out_degree(n))

        if fully_removed:
            print("-- fully removed member")

            in_edges = set(K.in_edges(n))
            out_edges = set(K.out_edges(n))

            fixed_edges = in_edges.intersection([(v, u) for u, v in out_edges])

            if fixed_edges:
                print("-- fixed member")
                edge_draw_settings(K, fixed_edges, "cut")

                for fixed_edge in fixed_edges:
                    fxd_n_cut_rmv.add(fixed_edge[1])  # fully remove the current node
                    fxd_n_cut.add(fixed_edge[0])  # other node is just cut, have to check it

    print("\nfixed nodes that are cut but not removed: {}".format(fxd_n_cut))
    print("fixed nodes that are cut and fully removed: {}".format(fxd_n_cut_rmv))

    return list(fxd_n_cut_rmv)


def check_fixed_nodes_support(G, K, rm_membs, fxd_n_cut_rmv):
    """
    STEP C: Check the support conditions for fixed nodes.

    Parameters:
    - G (networkx.Graph): The overall graph.
    - K (networkx.Graph): The subgraph for member removal.
    - rm_membs (list): List of nodes to be removed.
    - fxd_n_cut_rmv (list): List of fully removed fixed nodes.

    """
    print("\n\n2C. CHECK FIXED NODES SUPPORTS")

    n_1side_fxd = []
    n_2side_fxd = []

    for n_check in K.nodes():
        node_type = _check_node_type(G, n_check, rm_membs)

        if node_type in ["end_2sides_fixed"]:
            n_2side_fxd.append(n_check)
        elif node_type in ["danger_1side_fixed"]:
            n_1side_fxd.append(n_check)

    fxd_n_check = n_1side_fxd + n_2side_fxd

    print("\n-- NODES fully removed fixed: {}".format(fxd_n_cut_rmv))
    print("-- NODES to check, 1-side + 2-side fixed: {} {}".format(n_1side_fxd, n_2side_fxd))

    # check that properly supported
    n_safe_fix1, n_safe_fix2, n_notsafe = _check_connected(G, K, fxd_n_cut_rmv, fxd_n_check)

    node_draw_settings(K, n_safe_fix1, "end_1sides_fixed")
    node_draw_settings(K, n_safe_fix2, "end_2sides_fixed")
    node_draw_settings(K, n_notsafe, "danger_1side_fixed")
    node_draw_settings(K, fxd_n_cut_rmv, "normal_1side_fixed")
    node_draw_settings(K, rm_membs, "remove")


if __name__ == "__main__":
    pass
