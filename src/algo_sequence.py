import networkx as nx

from src.algorithms import (
    node_draw_settings,
    _count_fixed_sides,
)


def _make_graph_title(step, nodes):
    len_nodes = len(nodes)

    if len_nodes == 2:
        text = "Step {}: {} and {}".format(step, nodes[0], nodes[1])
    elif len_nodes == 1:
        text = "Step {}: {}".format(step, nodes[0])
    else:
        print("ERROR, IN MAKE_GRAPH_TITLE")

    return text


def _update_rm_list(node_remove_step, rm_membs):
    """is an active member removed in this step, if so remove"""
    node_remove_step = list(node_remove_step)

    if rm_membs:
        for n in node_remove_step:
            if n == rm_membs[0]:
                print(f"--an active remove member, {n}, is removed")
                rm_membs.remove(n)
                break

    return rm_membs


def _remove_disconnected_graphs(K):
    nodes_remove_disconnected = []
    components = list(nx.weakly_connected_components(K))
    desired_n_types = ["end_2sides_fixed", "end_1sides_fixed", "end_foundation"]

    for i, component in enumerate(components):
        print("check connected component: {}".format(i + 1))

        # Check if all nodes in the component have specific node types
        if all(K.nodes[n]["node_type"] in desired_n_types for n in component):
            nodes_remove_disconnected.extend(list(component))
            print(f"--Component of only fixed nodes: {nodes_remove_disconnected}")

    K.remove_nodes_from(nodes_remove_disconnected)


def _relabel_graph(K, rm_membs):
    # Re-label a node if it is now free from supporting others
    for n in K.nodes():
        n_type = K.nodes[n]["node_type"]
        in_deg = K.in_degree(n)
        num_fixed_sides = _count_fixed_sides(K, n)[0]

        if (
            (in_deg == 0 and n_type == "normal")
            or (in_deg == 0 and n_type == "remove" and n == rm_membs[0])
            or (in_deg == 1 and n_type == "remove" and n == rm_membs[0] and num_fixed_sides == 1)
            or (in_deg == 1 and n_type == "normal_1side_fixed")
        ):
            node_draw_settings(K, n, "start")

    # re-run again, if "normal_1side_fixed" --> "start" in previous
    # now "remove" --> "start" if the "normal_1side_fixed" on top will also be removed
    for n in K.nodes():
        n_type = K.nodes[n]["node_type"]
        in_deg = K.in_degree(n)

        if (
            in_deg == 1
            and n_type == "remove"
            and K.nodes[list(K.predecessors(n))[0]]["node_type"] == "start"
            and n == rm_membs[0]
        ):
            node_draw_settings(K, n, "start")


def _relabel_graph_ending(K):
    desired_n_types = ["end_2sides_fixed", "end_1sides_fixed", "end_foundation", "normal"]

    if all(K.nodes[n]["node_type"] in desired_n_types for n in K.nodes()):
        for n in K.nodes():
            if K.nodes[n]["node_type"] == "normal":
                node_draw_settings(K, n, "start")


def _relabel_graph_fixed(K):
    """make start node if only end node on top and no other start members in graph
    algo will terminate otherwise
    """
    desired_n_types = ["end_2sides_fixed", "end_1sides_fixed", "end_foundation"]

    if "start" not in [K.nodes[n]["node_type"] for n in K.nodes()]:
        for n in K.nodes():
            node_type = K.nodes[n]["node_type"]
            in_deg_norm = K.in_degree(n) - _count_fixed_sides(K, n)[0]
            n_predeces = list(K.predecessors(n))

            cnt_fxd_ontop = sum(1 for k in n_predeces if K.nodes[k]["node_type"] in desired_n_types)

            if node_type in ["normal", "normal_1side_fixed"] and in_deg_norm == cnt_fxd_ontop:
                node_draw_settings(K, n, "start")


###############################################


def find_n_to_rmv(K, n_type):
    n_rmv = [
        n for n, data in K.nodes(data=True) if "node_type" in data and data["node_type"] == n_type
    ]

    n_rmv = sorted(n_rmv, key=lambda x: x[1])

    return n_rmv


def select_n_subset(n_rmv, num_agents):
    num_nodes_to_remove = len(n_rmv)

    if num_nodes_to_remove > num_agents:
        user_input = input("choose members {}: int int ".format(n_rmv))
        input_list_str = user_input.split()

        try:
            # Convert each string element to an integer
            input_list_int = [int(x) for x in input_list_str]
        except ValueError:
            print("Invalid input. Please enter a valid list of integers.")

    elif num_nodes_to_remove == num_agents:
        input_list_int = list(range(0, num_agents))
    else:
        input_list_int = list(range(0, num_nodes_to_remove))

    input_list_int.sort(reverse=True)  # avoid index shift when remove
    n_rmv_step = [n_rmv.pop(index) for index in input_list_int]

    return n_rmv_step


def crnt_subg_process(K, n_rmv_step, rm_membs, rmv_disconnect=False):
    K.remove_nodes_from(n_rmv_step)
    rm_membs = _update_rm_list(n_rmv_step, rm_membs)

    if rmv_disconnect:
        _remove_disconnected_graphs(K)


def crnt_subg_save(K, step, n_rmv_step, saved_K, saved_seq):
    K.graph["title"] = _make_graph_title(step, n_rmv_step)
    saved_K.append(K.copy())
    saved_seq.append(n_rmv_step)


def new_subg_relabel(K, rm_membs):
    _relabel_graph(K, rm_membs)
    _relabel_graph_ending(K)
    _relabel_graph_fixed(K)
