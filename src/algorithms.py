import imp
import networkx as nx
from src.drawing import node_settings, edge_settings


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


def initialize(G, remove_node):

    """
    initialize the algorithm with the node to be removed
    """

    nodes_saved = []
    nodes_queue = []

    print("\nINITIALIZING WITH NODE {}".format(remove_node))
    node_settings(G, [remove_node], "remove")

    if len(G.in_edges(remove_node)) == 0:
        print("--NO ADD: start node")
    elif len(G.out_edges(remove_node)) == 0:
        print("--NO ADD: end node")
    else:
        nodes_queue, nodes_saved = find_adjacent_nodes(G, remove_node, nodes_queue, nodes_saved)

    nodes_saved.append(remove_node)

    return nodes_saved, nodes_queue


def add_node_to_queue(G, n, two_side_fixed, one_side_fixed, remove_node):
    print("Check if the node should be added to queue")

    add = False

    if len(G.in_edges(n)) == 0:
        print("--NO ADD: start node")
        node_settings(G, [n], "start")
    elif len(G.out_edges(n)) == 0:
        print("--NO ADD: end node")
        node_settings(G, [n], "end")
    elif count_fixed_sides(G, n)[0] == 2:
        print("--NO ADD: fixed on TWO sides")
        two_side_fixed.append(n)
        node_settings(G, [n], "end")
    elif count_fixed_sides(G, n)[0] == 1:
        print("--FIXED NODE, fixed on ONE side")

        if G.has_edge(n, remove_node) and not check_if_fixed_exists(G, n, remove_node):
            print("-- -- ADD: normal node, since resting on member to remove")
            add = True  # make a normal node if it's resting on to remove
            node_settings(G, [n], "normal")
        else:
            print("-- -- NO ADD: not direct resting on member to remove")
            one_side_fixed.append(n)
            node_settings(G, [n], "danger")

    else:
        print("--ADD: normal node")
        add = True
        node_settings(G, [n], "normal")

    return add


def check_cut(G, K):
    """
    See if the subgraph K fully contains the edges attached to a member

    If a member is fully removed then it must be manually cut if it has a fixed connection

    Return the node that has a fixed connection cut, to be checked if requiring support
    """

    print("\n2. CHECK WHAT EDGES NEED TO BE CUT")
    nodes_cut = []
    nodes_fully_removed = []

    for n in K.nodes():
        print("\n--checking node {}".format(n))
        e_total_K = len(_get_e_out(K, n)) + len(_get_e_in(K, n))
        e_total_G = len(_get_e_out(G, n)) + len(_get_e_in(G, n))

        if e_total_K == e_total_G:
            print("-- --fully removed")

            num_e_fixed, e_fixed = count_fixed_sides(K, n)

            if num_e_fixed:  # if there are any fixed edges

                for e in e_fixed:
                    print("-- --fixed connection to cut {}".format(e))

                    nodes_cut.append(e[1])
                    nodes_fully_removed.append(e[0])

                    edge_settings(K, [e], "cut")
                    # node_settings(K,[e[0]],"normal")

            else:
                print("-- --no connection to cut")

        else:
            print("-- --partially removed")

    print("\nnodes that need to be cut: {}".format(nodes_cut))
    print("nodes that are fully removed: {}".format(nodes_fully_removed))

    return nodes_cut, nodes_fully_removed


def check_connected(G, K, nodes_fully_removed, nodes_check_support):
    """
    check if a member with a single fixed has at least TWO other support connections after the removal of the member.
    If it is fixed and not being cut then it just needs 1 additional connection.

    If it has enough edges it is considered fixed support in this disassembly step
    """

    print(
        "\n3. CHECKING NODES {} in SUBGRAPH K IF THEY HAVE ENOUGH SUPPORT".format(
            nodes_check_support
        )
    )

    for n in nodes_check_support:
        print("\nCHECK NODE {}".format(n))

        e_G = _get_e_out(G, n)  # starting members supported by
        e_K = _get_e_out(K, n)  # supporting members to remove

        num_supports = len(e_G) - len(e_K)
        print("-- {} supports left. These members being removed: {}".format(num_supports, e_K))

        # if fixed edge is not being cut, add back
        for e in e_K:
            if check_if_fixed_exists(G, e[0], e[1]):
                if e[0] in nodes_fully_removed or e[1] in nodes_fully_removed:
                    print("-- fixed is cut, do not add back in")
                else:
                    print("-- fixed is not cut, add support back in")
                    num_supports += 1

        if num_supports < 2:
            print("-- DANGER, only {} SUPPORTS".format(num_supports))
            node_settings(K, [n], "danger")
        else:
            print("-- SAFE, w/ {} SUPPORTS".format(num_supports))
            node_settings(K, [n], "end")

        if n in nodes_fully_removed:
            print("-- SAFE, FULLY REMOVE")
            node_settings(K, [n], "normal")

    return K


def single_member_remove(G, rm):

    nodes_saved, nodes_queue = initialize(G, rm)
    two_side_fixed = []
    one_side_fixed = []

    print("current n_queue: ", nodes_queue)
    print("current n_saved: ", nodes_saved)

    # 1. see what nodes to add
    while nodes_queue:
        n = nodes_queue.pop(0)
        print("\n\nCHECKING NODE {}".format(n))

        if add_node_to_queue(G, n, two_side_fixed, one_side_fixed, rm):
            nodes_queue, nodes_saved = find_adjacent_nodes(G, n, nodes_queue, nodes_saved)

        nodes_saved.append(n)
        print("current n_queue: ", nodes_queue)
        print("current n_saved: ", nodes_saved)

    print("\nNODES IN FINAL SUBGRAPH:", nodes_saved)

    #### MODIFY K ######
    K = G.subgraph(nodes_saved)
    nx.set_edge_attributes(K, "black", "color")

    print("-- NODES one side fixed now: {}".format(one_side_fixed))
    print("-- NODES two side fixed: {}".format(two_side_fixed))

    # 2. check what needs to be cut
    nodes_cut, nodes_fully_removed = check_cut(G, K)

    nodes_fully_removed.append(rm)
    nodes_fully_removed = list(set(nodes_fully_removed))  # remove duplicates

    nodes_check_support = one_side_fixed + two_side_fixed + nodes_cut
    nodes_check_support = list(set(nodes_check_support))  # remove duplicates

    # dont check the node specified for removal
    if rm in nodes_check_support:
        nodes_check_support.remove(rm)

    print("-- NODES fully removed: {}".format(nodes_fully_removed))
    print("-- NODES to check support on: {}".format(nodes_check_support))

    # 3. check that properly supported
    K = check_connected(G, K, nodes_fully_removed, nodes_check_support)

    return K, nodes_check_support


def multi_member_remove(G, K, rms, nodes_check_support):

    print("\n1. SUBGRAPH CALC FOR MEMBERs: {}".format(rms))

    node_settings(K, rms, "remove")  # color all removal members

    #### MODIFY K ######
    print("-- NODES check support: {}".format(nodes_check_support))

    # 2. check what needs to be cut
    nodes_cut, nodes_fully_removed = check_cut(G, K)

    nodes_fully_removed.extend(rms)
    nodes_fully_removed = list(set(nodes_fully_removed))  # remove duplicates

    nodes_check_support.extend(nodes_cut)
    nodes_check_support = list(set(nodes_check_support))

    # dont check the node specified for removal
    for rm in rms:
        if rm in nodes_check_support:
            nodes_check_support.remove(rm)

    print("-- NODES fully removed: {}".format(nodes_fully_removed))
    print("-- NODES to check support on: {}".format(nodes_check_support))

    _ = check_connected(G, K, nodes_fully_removed, nodes_check_support)

    return K


if __name__ == "__main__":
    pass
