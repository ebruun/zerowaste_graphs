import imp
import networkx as nx
import copy
from src.drawing import node_draw_settings, edge_draw_settings


def _get_e_out(G, n):
    return list(G.out_edges(n))


def _get_e_in(G, n):
    return list(G.in_edges(n))


def _check_if_fixed_exists(G, n1, n2):
    if G.has_edge(n1, n2) and G.has_edge(n2, n1):
        return True
    else:
        return False


def count_fixed_sides(G, n):
    """
    Check on how many sides node is fixed

    return COUNT and FIXED_EDGES as tuple
    """

    fixed_e_count = 0
    e_fixed = []

    neighbors = list(G.neighbors(n))

    for neighbor in neighbors:
        if _check_if_fixed_exists(G, n, neighbor):
            fixed_e_count += 1
            e_fixed.append((n, neighbor))  # save as tuple ('n1','n2')

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


def _check_node_type(G, n_check, rm_memb):
    print("Check what type of member this is")

    if n_check == rm_memb:
        print("--REMOVE MEMBER")
        node_type = "remove"
    elif G.in_degree(n_check) == 0:
        print("--START NODE, in_degree=0")
        node_type = "start"
    elif G.out_degree(n_check) == 0:
        print("--END NODE, out_degree=0")
        node_type = "end"
    elif count_fixed_sides(G, n_check)[0] == 2:
        print("--END NODE, fixed on TWO sides")
        node_type = "end_2sides_fixed"
    elif count_fixed_sides(G, n_check)[0] == 1:
        if G.has_edge(n_check, rm_memb) and not _check_if_fixed_exists(G, n_check, rm_memb):
            print("-- NORMAL NODE, fixed on ONE side and on member to remove")
            node_type = "normal_1side_fixed"
        else:
            print("-- DANGER NODE, fixed on ONE side but not resting on member to remove")
            node_type = "danger_1side_fixed"
    else:
        print("-- NORMAL NODE")
        node_type = "normal"

    return node_type


def _check_cut(G, K):
    """
    Check if a member is fully removed, check if it is a fixed member
    If yes to both, then it has to be manually cut from the structure
    Return the nodes that have a fixed connection cut, partial or fully removed
    """

    print("\n2. CHECK WHAT FIXED EDGES NEED TO BE CUT")

    n_fixed_cut = set()
    n_fixed_fully_removed = set()

    for n in K.nodes():
        print("\nchecking node {}".format(n))

        fully_removed = (K.in_degree(n) + K.out_degree(n)) == (G.in_degree(n) + G.out_degree(n))

        if fully_removed:
            print("-- fully removed")

            in_edges = set(K.in_edges(n))
            out_edges = set(K.out_edges(n))

            fixed_edges = in_edges.intersection([(v, u) for u, v in out_edges])

            if fixed_edges:
                print("-- fixed node")

                for fixed_edge in fixed_edges:
                    n_fixed_fully_removed.add(fixed_edge[1])
                    n_fixed_cut.add(fixed_edge[0])
                    edge_draw_settings(K, [fixed_edge], "cut")

    print("\nfixed nodes that are cut but not removed: {}".format(n_fixed_cut))
    print("fixed nodes that are cut and fully removed: {}".format(n_fixed_fully_removed))

    return list(n_fixed_cut), list(n_fixed_fully_removed)


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
            if _check_if_fixed_exists(G, e[0], e[1]):
                if e[0] in nodes_fully_removed or e[1] in nodes_fully_removed:
                    print("-- fixed is cut, do not add back in")
                else:
                    print("-- fixed is not cut, add support back in")
                    num_supports += 1

        if num_supports < 2:
            print("-- DANGER, only {} SUPPORTS".format(num_supports))
            node_draw_settings(K, [n], "danger")
        else:
            print("-- SAFE, w/ {} SUPPORTS".format(num_supports))
            node_draw_settings(K, [n], "end")

        if n in nodes_fully_removed:
            print("-- SAFE, FULLY REMOVE")
            node_draw_settings(K, [n], "normal")

    return K


def calc_subg(G, rm_memb):
    "calculate a sub-graph based on the member set for removal"

    nodes_queue = [rm_memb]  # queue to check
    nodes_checked = []  # saved list of checked nodes

    # A. Loop through nodes queue, and see if their adjacents should be added
    while nodes_queue:
        n_check = nodes_queue.pop(0)
        print("\n\nCHECKING NODE {}".format(n_check))

        node_type = _check_node_type(G, n_check, rm_memb)

        if node_type in ["remove", "normal", "normal_1side_fixed"]:
            nodes_queue, nodes_checked = find_adjacent_nodes(G, n_check, nodes_queue, nodes_checked)

        nodes_checked.append(n_check)
        node_draw_settings(G, [n_check], node_type)

        print("current n_queue: ", nodes_queue)
        print("current n_saved: ", nodes_checked)

    print("\nNODES IN FINAL SUBGRAPH:", nodes_checked)

    K = G.subgraph(nodes_checked)  # sub-graph built from checked nodes
    nx.set_edge_attributes(K, "black", "color")

    return K


def check_fixed_nodes_cut(G, K):
    """
    Check if a member is fully removed, check if it is a fixed member
    If yes to both, then it has to be manually cut from the structure
    Return the nodes that have a fixed connection cut, partial or fully removed
    """

    print("\n2. CHECK WHAT FIXED EDGES NEED TO BE CUT")

    fixed_nodes_cut = set()
    fixed_nodes_fully_removed = set()

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

                for fixed_edge in fixed_edges:
                    fixed_nodes_fully_removed.add(fixed_edge[1])  # fully remove the current node
                    fixed_nodes_cut.add(fixed_edge[0])  # other node is just cut, have to check it
                    edge_draw_settings(K, [fixed_edge], "cut")

    print("\nfixed nodes that are cut but not removed: {}".format(fixed_nodes_cut))
    print("fixed nodes that are cut and fully removed: {}".format(fixed_nodes_fully_removed))

    fixed_nodes_cut = list(fixed_nodes_cut)
    fixed_nodes_fully_removed = list(fixed_nodes_fully_removed)

    return K, fixed_nodes_cut, fixed_nodes_fully_removed


def check_support(G, K, rm_memb, fixed_nodes_cut, fixed_nodes_fully_removed):
    two_side_fixed = []
    one_side_fixed = []

    for n_check in K.nodes():
        print("\n\nCHECKING NODE {}".format(n_check))
        node_type = _check_node_type(G, n_check, rm_memb)

        if node_type in ["end_2sides_fixed"]:
            two_side_fixed.append(n_check)
        elif node_type in ["danger_1side_fixed"]:
            one_side_fixed.append(n_check)

    print("-- NODES one side fixed now: {}".format(one_side_fixed))
    print("-- NODES two side fixed: {}".format(two_side_fixed))

    fixed_nodes_fully_removed.append(rm_memb)
    fixed_nodes_fully_removed = list(set(fixed_nodes_fully_removed))  # remove duplicates

    nodes_check_support = one_side_fixed + two_side_fixed + fixed_nodes_cut
    nodes_check_support = list(set(nodes_check_support))  # remove duplicates

    # dont check the node specified for removal
    if rm_memb in nodes_check_support:
        nodes_check_support.remove(rm_memb)

    print("-- NODES fully removed: {}".format(fixed_nodes_fully_removed))
    print("-- NODES to check support on: {}".format(nodes_check_support))

    # 3. check that properly supported
    K = check_connected(G, K, fixed_nodes_fully_removed, nodes_check_support)

    return K, nodes_check_support


def calc_multimemb_remove(G, K, rms, nodes_check_support):
    print("\n1. SUBGRAPH CALC FOR MEMBERs: {}".format(rms))

    node_draw_settings(K, rms, "remove")  # color all removal members

    #### MODIFY K ######
    print("-- NODES check support: {}".format(nodes_check_support))

    # 2. check what needs to be cut
    nodes_cut, nodes_fully_removed = _check_cut(G, K)

    nodes_fully_removed.extend(rms)
    nodes_fully_removed = list(set(nodes_fully_removed))  # remove duplicates

    nodes_check_support.extend(nodes_cut)
    nodes_check_support = list(set(nodes_check_support))  # remove duplicates

    # dont check the node specified for removal
    for rm in rms:
        if rm in nodes_check_support:
            nodes_check_support.remove(rm)

    print("-- NODES fully removed: {}".format(nodes_fully_removed))
    print("-- NODES to check support on: {}".format(nodes_check_support))

    K = check_connected(G, K, nodes_fully_removed, nodes_check_support)

    return K


if __name__ == "__main__":
    pass
