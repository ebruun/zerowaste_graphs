from os import remove
import networkx as nx


def _get_e_out(G, n):
    return list(G.out_edges(n))


def _get_e_in(G, n):
    return list(G.in_edges(n))


def check_if_fixed_exists(G, n1, n2):
    if G.has_edge(n1, n2) and G.has_edge(n2, n1):
        return True
    else:
        return False


def count_fixed_sides(G, n):
    """
    Check on how many sides node is fixed

    return COUNT and FIXED_EDGES
    """
    e_list = _get_e_out(G, n)

    fixed_e_count = 0
    e_fixed = []
    for e in e_list:
        if G.has_edge(e[1], e[0]):
            fixed_e_count += 1
            e_fixed.append(e)

    return fixed_e_count, e_fixed


def find_adjacent_nodes(G, n, n_queue, n_saved):
    e_in_normal = _get_e_in(G, n)
    e_out_normal = _get_e_out(G, n)

    new_n = []
    new_n.extend([e[0] for e in e_in_normal])
    new_n.extend([e[1] for e in e_out_normal])

    # don't add already visited or already in queue
    n_queue.extend(set(new_n) - set(n_saved).union(set(n_queue)))

    return n_queue, n_saved


def add_node_to_queue(G, n, two_side_fixed, one_side_fixed, remove_node):
    print("Check if the node should be added to queue")

    add = False

    if len(G.in_edges(n)) == 0:
        print("--NO ADD: start node")
        G.nodes[n]["color"] = "tab:green"
        G.nodes[n]["size"] = 300
    elif len(G.out_edges(n)) == 0:
        print("--NO ADD: end node")
        G.nodes[n]["color"] = "black"
    elif count_fixed_sides(G, n)[0] == 2:
        print("--NO ADD: fixed on TWO sides")
        G.nodes[n]["color"] = "black"
        G.nodes[n]["size"] = 500
        two_side_fixed.append(n)
    elif count_fixed_sides(G, n)[0] == 1:
        print("--FIXED NODE, fixed on ONE side")

        if G.has_edge(n, remove_node) and not check_if_fixed_exists(G, n, remove_node):
            print("-- -- ADD: normal node, since resting on member to remove")
            G.nodes[n]["color"] = "tab:grey"
            G.nodes[n]["size"] = 300
            add = True  # make a normal node if it's resting on to remove
        else:
            print("-- -- NO ADD: not direct resting on member to remove")
            G.nodes[n]["color"] = "orange"
            G.nodes[n]["size"] = 500
            one_side_fixed.append(n)
    else:
        print("--ADD: normal node")
        G.nodes[n]["color"] = "tab:grey"
        G.nodes[n]["size"] = 300
        add = True
    return add


# def remove_two_side_out(K, nodes, remove_node):

#     """remove redundant out edges from fixed nodes to other nodes in the graph,
#     unless they connect directly to the element to be removed
#     """

#     print("\nREMOVING SINGLE OUT EDGES FROM FIXED NODES {} in SUBGRAPH K".format(nodes))

#     K_copy = K.copy()

#     for n in nodes:
#         e_K = _get_e_out(K, n)

#         for e in e_K:

#             if not check_if_fixed_exists(K, e[1], e[0]) and remove_node not in e:
#                 print("single edge {}".format(e))
#                 K_copy.remove_edge(e[0], e[1])

#     return K_copy


def check_connected(G, K, remove_node, nodes):
    """
    check if a member with a single fixed has at least TWO other support connections after the removal of the member.
    If it is fixed and not being cut then it just needs 1 additional connection.

    If it has enough edges it is considered fixed support in this disassembly step
    """

    print("\n3. CHECKING FIXED NODES {} in SUBGRAPH K".format(nodes))

    for n in nodes:
        print("\n--CHECK NODE {}".format(n))
        e_G = _get_e_out(G, n)  # starting
        e_K = _get_e_out(K, n)  # how many members removed

        num_supports = len(e_G) - len(e_K)

        # if fixed edge is not being cut, add back
        for e in e_K:
            if check_if_fixed_exists(G, e[0], e[1]):
                if remove_node in e:
                    pass
                else:
                    num_supports += 1

        if num_supports < 2:
            print("--DANGER, only {} SUPPORTS".format(num_supports))
            K.nodes[n]["color"] = "orange"
            K.nodes[n]["size"] = 500
        else:
            print("--SAFE, w/ {} SUPPORTS".format(num_supports))
            K.nodes[n]["color"] = "black"
            K.nodes[n]["size"] = 500

    return K


def check_cut(G, K):
    """
    See if the subgraph K fully contains the edges attached to a member

    If a member is fully removed then it must be manually cut if it has a fixed connection

    Return the node that has a fixed connection cut, to be checked if requiring support
    """

    print("\n2. CHECK WHAT EDGES NEED TO BE CUT")
    nodes_cut = []

    for n in K.nodes():
        print("\n--checking node {}".format(n))
        e_total_K = len(_get_e_out(K, n)) + len(_get_e_in(K, n))
        e_total_G = len(_get_e_out(G, n)) + len(_get_e_in(G, n))

        if e_total_K == e_total_G:
            print("-- --fully removed")

            e_count, e_fixed = count_fixed_sides(K, n)

            if e_count:  # if there are any fixed edges

                for e in e_fixed:
                    print("-- --fixed connection to cut {}".format(e))
                    K.edges[e[0], e[1], 0]["edge_style"] = "dashed"
                    K.edges[e[0], e[1], 0]["weight"] = 1.5
                    K.edges[e[0], e[1], 0]["color"] = "tab:red"

                    K.edges[e[1], e[0], 0]["edge_style"] = "dashed"
                    K.edges[e[1], e[0], 0]["weight"] = 1.5
                    K.edges[e[1], e[0], 0]["color"] = "tab:red"

                    nodes_cut.append(e[1])

            else:
                print("-- --no connection to cut")

        else:
            print("-- --partially removed")

    return nodes_cut


def initialize(G, remove_node):

    """
    initialize the algorithm with the node to be removed
    """

    nodes_saved = []
    nodes_queue = []

    print("\nINITIALIZING WITH NODE {}".format(remove_node))
    G.nodes[remove_node]["color"] = "tab:red"
    G.nodes[remove_node]["size"] = 600
    G.nodes[remove_node]["node_shape"] = "8"

    if len(G.in_edges(remove_node)) == 0:
        print("--NO ADD: start node")
    elif len(G.out_edges(remove_node)) == 0:
        print("--NO ADD: end node")
    else:
        nodes_queue, nodes_saved = find_adjacent_nodes(G, remove_node, nodes_queue, nodes_saved)

    nodes_saved.append(remove_node)

    return nodes_saved, nodes_queue


def single_member_remove(G, remove_node):

    print("\n1. SUBGRAPH CALC FOR MEMBER: {}".format(remove_node))

    nodes_saved, nodes_queue = initialize(G, remove_node)

    print("current n_queue: ", nodes_queue)
    print("current n_saved: ", nodes_saved)

    two_side_fixed = []
    one_side_fixed = []

    while nodes_queue:
        n = nodes_queue.pop(0)
        print("\n\nCHECKING NODE {}".format(n))

        if add_node_to_queue(G, n, two_side_fixed, one_side_fixed, remove_node):
            nodes_queue, nodes_saved = find_adjacent_nodes(G, n, nodes_queue, nodes_saved)

        nodes_saved.append(n)
        print("current n_queue: ", nodes_queue)
        print("current n_saved: ", nodes_saved)

    print("\nNODES IN SUBGRAPH:", nodes_saved)

    K = G.subgraph(nodes_saved)
    nx.set_edge_attributes(K, "black", "color")

    # K = remove_two_side_out(K,two_side_fixed, remove_node)

    nodes_cut = check_cut(G, K)
    one_side_fixed.extend(nodes_cut)

    K = check_connected(G, K, remove_node, one_side_fixed)

    return K


if __name__ == "__main__":
    pass
