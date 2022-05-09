import networkx as nx


def _get_e_out(G, n):
    return list(G.out_edges(n))


def _get_e_in(G, n):
    return list(G.in_edges(n))


def check_if_fixed_two_sides(G, n):
    print("\nCheck if edge is fixed on two sides")

    e_list = _get_e_out(G, n)

    fixed_e_count = 0
    for e in e_list:
        if G.has_edge(e[1], e[0]):
            fixed_e_count += 1

    print("HOW MANY FIXED: ", fixed_e_count)


def check_if_normal_node(G, n):
    print("Check what kind of node")

    if len(G.in_edges(n)) == 0:
        print("--start node")
        G.nodes[n]["color"] = "grey"
        check = False
    elif len(G.out_edges(n)) == 0:
        print("--end node")
        G.nodes[n]["color"] = "black"
        check = False
    else:
        print("--normal node")
        check = True

        # if all outgoing edges are fixed (no normal edges)
        # otherwise a fixed node can get added into queue
        if not check_if_fixed_edge(G, _get_e_out(G, n))[0]:
            print("--normal node, but only fixed outgoing edges")
            G.nodes[n]["color"] = "black"
            check = False

        check_if_fixed_two_sides(G, n)

    return check


def check_if_fixed_edge(G, e_list):
    print("\nCheck if edge is fixed")

    e_normal = []
    e_fixed = []

    for e in e_list:
        if G.has_edge(e[1], e[0]):  # check if edge in opposite direction
            # print("--This is fixed edge",e)
            e_fixed.append(e)
        else:
            # print("--This is normal edge",e)
            e_normal.append(e)

    if not e_normal:
        print("--NO NORMAL EDGES")

    return e_normal, e_fixed


def find_adjacent_nodes(G, n, n_queue, n_saved):

    e_in_normal, e_in_fixed = check_if_fixed_edge(G, _get_e_in(G, n))
    print("--e in normal", e_in_normal)
    print("--e in fixed", e_in_fixed)

    e_out_normal, e_out_fixed = check_if_fixed_edge(G, _get_e_out(G, n))
    print("--e out normal", e_out_normal)
    print("--e out fixed", e_out_fixed)

    new_n = []
    new_n.extend([e[0] for e in e_in_normal])
    new_n.extend([e[1] for e in e_out_normal])

    # don't add already visited or already in queue
    n_queue.extend(set(new_n) - set(n_saved).union(set(n_queue)))

    new_n_fixed = []
    new_n_fixed.extend([e[0] for e in e_in_fixed])
    new_n_fixed.extend([e[1] for e in e_out_fixed])

    n_saved.extend(set(new_n_fixed) - set(n_saved))

    return n_queue, n_saved


def phase_1(G, start_node):

    print("\nSTART FOR MEMBER: {}".format(start_node))

    nodes_saved = []
    nodes_queue = [start_node]

    while nodes_queue:
        n = nodes_queue.pop(0)
        print("\n\nCHECKING NODE {}".format(n))

        if check_if_normal_node(G, n):
            nodes_queue, nodes_saved = find_adjacent_nodes(G, n, nodes_queue, nodes_saved)

        nodes_saved.append(n)
        print("current n_queue: ", nodes_queue)
        print("current n_saved: ", nodes_saved)

    print("\nNODES IN SUBGRAPH:", nodes_saved)
    return G.subgraph(nodes_saved)


if __name__ == "__main__":
    pass
