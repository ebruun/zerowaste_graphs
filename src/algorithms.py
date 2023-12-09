import imp
import networkx as nx
import copy
from src.drawing import node_draw_settings, edge_draw_settings


def _check_if_fixed_exists(G, n1, n2):
    if G.has_edge(n1, n2) and G.has_edge(n2, n1):
        return True
    else:
        return False


def _count_fixed_sides(G, n):
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


def _find_adjacent_nodes(G, n, n_queue, n_saved):
    e_in_normal = list(G.in_edges(n))
    e_out_normal = list(G.out_edges(n))

    new_n = []

    new_n.extend([e[0] for e in e_in_normal])
    new_n.extend([e[1] for e in e_out_normal])

    # don't add already visited or already in queue
    n_queue.extend(set(new_n) - set(n_saved).union(set(n_queue)))

    return n_queue, n_saved


def _check_node_type(G, n_check, rm_memb):
    print("\nCHECKING NODE TYPE OF: {}".format(n_check))

    if n_check == rm_memb and G.in_degree(n_check) == 0:
        print("--REMOVE & START NODE")
        node_type = "remove_start"
    elif n_check == rm_memb:
        print("--REMOVE NODE")
        node_type = "remove"
    elif G.in_degree(n_check) == 0:
        print("--START NODE, in_degree=0")
        node_type = "start"
    elif G.out_degree(n_check) == 0:
        print("--END NODE, out_degree=0")
        node_type = "end_foundation"
    elif _count_fixed_sides(G, n_check)[0] == 2:
        print("--END NODE, fixed on TWO sides")
        node_type = "end_2sides_fixed"
    elif _count_fixed_sides(G, n_check)[0] == 1:
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
        print("checking node {}".format(n))

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


def check_connected(G, K, fxd_n_cut_rmv, fxd_n_check):
    """
    check if fixed members have at least TWO other support connections after the removal of the member.
    If it is fixed (not being cut) then it just needs 1 additional connection for a total of 2
    If it has enough edges it is considered fixed support in this disassembly step
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
            if _count_fixed_sides(G, n)[0] == 1:
                n_safe_fix1.append(n)

    return n_safe_fix1, n_safe_fix2, n_notsafe


def calc_subg(G, rm_memb):
    "STEP A: calculate a sub-graph based on the member set for removal"

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


def check_fixed_nodes_cut(G, K):
    """
    STEP B:
    Check if a member in a subgraph is fully removed, check if it is a fixed member
    If yes to both, then it has to be manually cut from the structure
    Return the nodes that have a fixed connection cut, partial or fully removed
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

                for fixed_edge in fixed_edges:
                    fxd_n_cut_rmv.add(fixed_edge[1])  # fully remove the current node
                    fxd_n_cut.add(fixed_edge[0])  # other node is just cut, have to check it
                    edge_draw_settings(K, [fixed_edge], "cut")

    print("\nfixed nodes that are cut but not removed: {}".format(fxd_n_cut))
    print("fixed nodes that are cut and fully removed: {}".format(fxd_n_cut_rmv))

    # return list(fxd_n_cut), list(fxd_n_cut_rmv)
    return list(fxd_n_cut_rmv)


def check_fixed_nodes_support(G, K, rm_memb, fxd_n_cut_rmv):
    """
    STEP C:
    """
    print("\n\n2C. CHECK FIXED NODES SUPPORTS")

    n_1side_fxd = []
    n_2side_fxd = []

    for n_check in K.nodes():
        node_type = _check_node_type(G, n_check, rm_memb)

        if node_type in ["end_2sides_fixed"]:
            n_2side_fxd.append(n_check)
        elif node_type in ["danger_1side_fixed"]:
            n_1side_fxd.append(n_check)

    fxd_n_check = n_1side_fxd + n_2side_fxd

    print("\n-- NODES fully removed fixed: {}".format(fxd_n_cut_rmv))
    print("-- NODES to check, 1-side + 2-side fixed: {} {}".format(n_1side_fxd, n_2side_fxd))

    # check that properly supported
    n_safe_fix1, n_safe_fix2, n_notsafe = check_connected(G, K, fxd_n_cut_rmv, fxd_n_check)

    node_draw_settings(K, n_safe_fix1, "end_1sides_fixed")
    node_draw_settings(K, n_safe_fix2, "end_2sides_fixed")
    node_draw_settings(K, n_notsafe, "danger_1side_fixed")

    return fxd_n_check


def calc_multimemb_remove(G, K, rm_membs, nodes_check_support):
    print("\nSUBGRAPH CALC FOR MEMBERs: {}".format(rm_membs))

    node_draw_settings(K, rm_membs, "remove")  # color all removal members

    #### MODIFY K ######
    print("-- NODES check support: {}".format(nodes_check_support))

    # 2. check what needs to be cut
    nodes_cut, nodes_fully_removed = _check_cut(G, K)

    nodes_fully_removed.extend(rm_membs)
    nodes_fully_removed = list(set(nodes_fully_removed))  # remove duplicates

    nodes_check_support.extend(nodes_cut)
    nodes_check_support = list(set(nodes_check_support))  # remove duplicates

    # dont check the node specified for removal
    for rm in rm_membs:
        if rm in nodes_check_support:
            nodes_check_support.remove(rm)

    print("-- NODES fully removed: {}".format(nodes_fully_removed))
    print("-- NODES to check support on: {}".format(nodes_check_support))

    n_safe_fix1, n_safe_fix2, n_notsafe = check_connected(
        G, K, nodes_fully_removed, nodes_check_support
    )

    # node_draw_settings(K, n_safe_fix1, "end_1sides_fixed")
    # node_draw_settings(K, n_safe_fix2, "end_2sides_fixed")
    # node_draw_settings(K, n_notsafe, "danger_1side_fixed")

    return K


if __name__ == "__main__":
    pass
