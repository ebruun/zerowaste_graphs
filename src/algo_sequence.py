import networkx as nx

from src.algorithms import (
    node_draw_settings,
    _count_fixed_sides,
)


def _calc_steps(nodes_to_process, num_agents):
    tuple_list = [
        list(nodes_to_process[i : i + num_agents])
        for i in range(0, len(nodes_to_process), num_agents)
    ]

    return tuple_list


def calc_nodes_to_process(K, node_type, num_agents):
    nodes_to_process = [
        node
        for node, data in K.nodes(data=True)
        if "node_type" in data and data["node_type"] == node_type
    ]

    # sort based on 2nd letter of each entry
    nodes_to_process = sorted(nodes_to_process, key=lambda x: x[1])

    # steps = _calc_steps(nodes_to_process, num_agents)

    return nodes_to_process  # take only first set if more than one


def make_graph_title(step, nodes):
    len_nodes = len(nodes)

    if len_nodes == 2:
        text = "Step {}: {} and {}".format(step, nodes[0], nodes[1])
    elif len_nodes == 1:
        text = "Step {}: {}".format(step, nodes[0])
    else:
        print("ERROR, IN MAKE_GRAPH_TITLE")

    return text


def update_rm_list(node_remove_step, rm_membs):
    """is an active member removed in this step, if so remove"""
    node_remove_step = list(node_remove_step)

    if rm_membs:
        for n in node_remove_step:
            if n == rm_membs[0]:
                print(f"an active remove member, {n}, is removed")
                rm_membs.remove(n)
                break

    return rm_membs


def remove_disconnected_graphs(K):
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


def relabel_graph(K, rm_membs):
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


def relabel_graph_ending(K):
    desired_n_types = ["end_2sides_fixed", "end_1sides_fixed", "end_foundation", "normal"]

    if all(K.nodes[n]["node_type"] in desired_n_types for n in K.nodes()):
        for n in K.nodes():
            if K.nodes[n]["node_type"] == "normal":
                node_draw_settings(K, n, "start")


def relabel_graph_fixed(K):
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
