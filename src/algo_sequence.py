import networkx as nx

from src.algorithms import (
    node_draw_settings,
    _count_fixed_sides,
)


def _make_graph_title(step, nodes, nodes_robfxd):
    n_rmv = len(nodes)
    n_sup = len(nodes_robfxd)

    if n_rmv == 2 and n_sup == 0:
        text = "Step {}: {} (rm) & {} (rm)".format(step, nodes[0], nodes[1])
    elif n_rmv == 1 and n_sup == 0:
        text = "Step {}: {} (rm)".format(step, nodes[0])
    elif n_rmv == 0 and n_sup == 1:
        text = "Step {}: {} (rs)".format(step, nodes_robfxd[0])
    elif n_rmv == 0 and n_sup == 2:
        text = "Step {}: {} (rs) & {} (rs)".format(step, nodes_robfxd[0], nodes_robfxd[1])
    elif n_rmv == 1 and n_sup == 1:
        text = "Step {}: {} (rm) & {} (rs)".format(step, nodes[0], nodes_robfxd[0])
    elif n_rmv == 2 and n_sup == 1:
        text = "Step {}: {} (rm) & {} (rm) {} (rs)".format(
            step, nodes[0], nodes[1], nodes_robfxd[0]
        )
    elif n_rmv == 1 and n_sup == 2:
        text = "Step {}: {} (rm) & {} (rs) {} (rs)".format(
            step, nodes[0], nodes_robfxd[0], nodes_robfxd[1]
        )
    else:
        text = "none"

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


def _relabel_graph_ending(K):
    "if only these left, then make normal nodes = start nodes"
    desired_n_types = ["end_2sides_fixed", "end_1sides_fixed", "end_foundation", "normal"]

    if all(K.nodes[n]["node_type"] in desired_n_types for n in K.nodes()):
        for n in K.nodes():
            if K.nodes[n]["node_type"] == "normal":
                node_draw_settings(K, n, "start")


def _relabel_graph_robsupport(K):
    desired_n_types = ["end_2sides_fixed", "end_1sides_fixed", "end_foundation", "robsupport_fixed"]
    ignore_n_types = ["end_2sides_fixed", "end_1sides_fixed", "robsupport_fixed", "end_foundation"]

    for n in K.nodes():
        n_type = K.nodes[n]["node_type"]
        in_deg = K.in_degree(n)
        predecessors = list(K.predecessors(n))

        # edge case, if on top is only rob_support
        if (
            in_deg == 1
            and n_type not in ignore_n_types
            and K.nodes[predecessors[0]]["node_type"] == "robsupport_fixed"
        ):
            print("-- make {} start, one fxd predecessors = {}".format(n, predecessors))
            node_draw_settings(K, n, "start")

        # edge case, if on top is rob_support and end
        if in_deg == 2 and n_type not in ignore_n_types:
            attribute_values = [K.nodes[predecessor]["node_type"] for predecessor in predecessors]

            if set(attribute_values).issubset(desired_n_types):
                print("-- make {} start, two fxd predecessors = {}".format(n, predecessors))
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
        n for n, data in K.nodes(data=True) if "node_type" in data and data["node_type"] in n_type
    ]

    n_rmv = sorted(n_rmv, key=lambda x: x[1])

    return n_rmv


def select_n_support():
    user_input = input("Do you want to add support? (Y/N): ").strip().lower()

    if user_input == "y":
        return True
    else:
        return False


def which_n_support(K):
    user_input = input("what nodes are robot supported? ")
    input_list_str = user_input.split()

    for n in input_list_str:
        node_draw_settings(K, n, "robsupport_fixed")

    return input_list_str


def select_n_active(n_rmv):
    # Select for remove
    user_string = "choose members {}: int ... int ".format(n_rmv)
    user_input = input(user_string)
    rmv_indexes_str = user_input.split()

    try:
        # Convert each string element to an integer
        rmv_indexes_int = [int(x) for x in rmv_indexes_str]
    except ValueError:
        print("Invalid input. Please enter a valid list of integers.")

    rmv_indexes_int.sort(reverse=True)  # avoid index shift when remove
    n_rmv_select = [n_rmv.pop(index) for index in rmv_indexes_int]

    # Select for rob support
    user_string = "is {} rob_fixed: int ... int "
    user_input = input(user_string.format(n_rmv_select))
    robfxd_indexes_str = user_input.split()

    try:
        # Convert each string element to an integer
        robfxd_indexes_int = [int(x) for x in robfxd_indexes_str]
    except ValueError:
        print("Invalid input. Please enter a valid list of integers.")

    robfxd_indexes_int.sort(reverse=True)  # avoid index shift when remove
    n_robfxd_select = [n_rmv_select.pop(index) for index in robfxd_indexes_int]

    print(f"-Processing nodes: {n_rmv_select}")
    print(f"-robfixed nodes: {n_robfxd_select}")

    return n_rmv_select, n_robfxd_select


def crnt_subg_setrobfxd(K, n_robfxd_step):
    if n_robfxd_step:
        for n in n_robfxd_step:
            node_draw_settings(K, n, "robsupport_fixed")


def crnt_subg_process(K, n_rmv_step, rm_membs, rmv_disconnect=False):
    K.remove_nodes_from(n_rmv_step)
    rm_membs = _update_rm_list(n_rmv_step, rm_membs)

    if rmv_disconnect:
        _remove_disconnected_graphs(K)


def crnt_subg_save(K, step, n_rmv_step, n_robfxd_step, saved_K, saved_seq):
    K.graph["title"] = _make_graph_title(step, n_rmv_step, n_robfxd_step)

    saved_K.append(K.copy())
    saved_seq.append(n_rmv_step)


def new_subg_relabel(K, rm_membs):
    _relabel_graph(K, rm_membs)
    _relabel_graph_ending(K)
    _relabel_graph_fixed(K)
    _relabel_graph_robsupport(K)
