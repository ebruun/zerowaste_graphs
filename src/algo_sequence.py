import networkx as nx

from src.algorithms import (
    node_draw_settings,
)


def calc_nodes_to_process(K, node_type):
    nodes_to_process = [
        node
        for node, data in K.nodes(data=True)
        if "node_type" in data and data["node_type"] == node_type
    ]

    # sort based on 2nd letter of each entry
    nodes_to_process = sorted(nodes_to_process, key=lambda x: x[1])

    return nodes_to_process


def calc_steps(nodes_to_process, num_agents):
    tuple_list = [
        tuple(nodes_to_process[i : i + num_agents])
        for i in range(0, len(nodes_to_process), num_agents)
    ]

    return tuple_list


def remove_disconnected_graphs(K):
    nodes_remove_disconnected = []
    components = list(nx.weakly_connected_components(K))

    for i, component in enumerate(components):
        print("check connected component: {}".format(i + 1))
        # flag = True

        # Check if all nodes in the component have specific node types
        if all(
            K.nodes[n]["node_type"] in ["end_2sides_fixed", "end_1sides_fixed", "end_foundation"]
            for n in component
        ):
            nodes_remove_disconnected.extend(list(component))
            print(f"--Component of only fixed nodes: {nodes_remove_disconnected}")

    K.remove_nodes_from(nodes_remove_disconnected)


def relabel_graph(K, rm_membs):
    # Re-label a node if it is now free from supporting others
    for n in K.nodes():
        node_type = K.nodes[n]["node_type"]
        in_degree = K.in_degree(n)

        if in_degree == 0 and node_type == "normal":
            node_draw_settings(K, n, "start")

        if in_degree == 0 and node_type == "remove":
            if n == rm_membs[0]:
                node_draw_settings(K, n, "start")

        if in_degree == 1 and node_type == "normal_1side_fixed":
            node_draw_settings(K, n, "start")

    # re-run again, if "normal_1side_fixed" --> "normal" in previous
    # now "remove" --> "normal" if the "normal_1side_fixed" on top will be removed
    for n in K.nodes():
        node_type = K.nodes[n]["node_type"]
        in_degree = K.in_degree(n)

        if in_degree == 1 and node_type == "remove":
            u = list(K.predecessors(n))[0]

            if K.nodes[u]["node_type"] == "start" and n == rm_membs[0]:
                node_draw_settings(K, n, "start")


def check_if_remove_node(node_remove_step, rm_membs):
    node_remove_step = list(node_remove_step)

    for n in node_remove_step:
        if n == rm_membs[0]:
            print("a remove member {n} is removed")
            rm_membs.remove(n)

    return rm_membs
