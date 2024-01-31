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


def find_n_active(K, n_type):
    n_rmv = [
        n for n, data in K.nodes(data=True) if "node_type" in data and data["node_type"] in n_type
    ]

    n_rmv = sorted(n_rmv, key=lambda x: x[1])

    return n_rmv


def set_rob_support(K):
    user_input = input("Do you want to add rob support? (Y/N): ").strip().lower()

    if user_input == "y":
        user_input = input("what nodes are robot supported? ")
        input_list_str = user_input.split()

        for n in input_list_str:
            node_draw_settings(K, n, "robsupport_fixed")

    else:
        input_list_str = []

    return input_list_str


def select_n_active(K, n_active, n2):
    # if it's empty
    if not n_active:
        n_active = n2

    # if a member was user-specified at start
    if n2:
        str1 = "{} just supported, ".format(n2)
    else:
        str1 = "nothing just supported, "

    ### REMOVE
    user_string = "{}choose idx of RMV members {}: int ... int ".format(str1, n_active)
    user_input = input(user_string)

    indexes_str = user_input.split()
    indexes_int = [int(x) for x in indexes_str]

    n_rmv_select = [n_active[i] for i in indexes_int]

    ### SUPPORT
    # choose items not in already supported in user specified
    n_active2 = [item for item in n_active if item not in n2]

    # choose from items not already removed
    if n_rmv_select:
        str2 = "{} just removed, ".format(n_rmv_select)
        n_active2 = [item for item in n_active2 if item not in n_rmv_select]
    else:
        str2 = "nothing just removed, "

    user_string = "{}{}choose idx of SUPPORT members {}: int ... int ".format(str1, str2, n_active2)
    user_input = input(user_string)

    indexes_str = user_input.split()
    indexes_int = [int(x) for x in indexes_str]

    n_support_select = [n_active2[i] for i in indexes_int]
    n_support_select.extend(n2)

    n_support_select = [item for item in n_support_select if item not in n_rmv_select]

    # update graph output
    if n_support_select:
        for n in n_support_select:
            node_draw_settings(K, n, "robsupport_fixed")

    if n_rmv_select:
        for n in n_rmv_select:
            node_draw_settings(K, n, "start")

    print("In this step: {} removed, {} supported".format(n_rmv_select, n_support_select))

    return n_rmv_select, n_support_select


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
    K.graph["step"] = step

    saved_K.append(K.copy())
    saved_seq.append(n_rmv_step)


def new_subg_relabel(K, rm_membs):
    _relabel_graph(K, rm_membs)
    _relabel_graph_ending(K)
    _relabel_graph_fixed(K)
    _relabel_graph_robsupport(K)
