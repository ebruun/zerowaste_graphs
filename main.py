from src.build import (
    bld_g_full,
    bld_subg_single_remove,
    bld_subg_multi,
)

from src.drawing import draw_graph


def check_list():
    pass


def calculate_sequence(K):
    print("\nCALCULATING DISASSEMBLY SEQUENCE")

    nodes = list(K.nodes)
    sequence = []

    print(nodes)

    remove = []
    # check for any start/end nodes
    for n in nodes:
        c = K.nodes[n]["color"]

        if c == "tab:green":
            print("{} is a START node".format(n))
            sequence.append(n)
            remove.append(n)
        elif c == "black":
            print("{} is a END node".format(n))
            remove.append(n)

    nodes_left = list(set(nodes) - set(remove))

    print("remaining is {}".format(nodes_left))
    print("sequence is {}".format(sequence))


if __name__ == "__main__":
    phase_number = 1
    f_in = "P{}_data_in".format(phase_number)
    f_out = "P{}_graphs_out".format(phase_number)

    # Task #1: Building Overall Support Hierarchy
    G = bld_g_full(f_in)

    draw_graph(
        G=G,
        filepath="{}/{}".format(f_out, "_full_structure.png"),
        scale=1,
        plt_show=False,
        plt_save=False,
    )

    # Task #2: Single Member Removal Sub-graphs
    # rm_membs = ["SP1_2", "SP1_3", "SP1_4", "ES10"]
    # rm_membs = ["SS1", "WS9", "WP1_3", "SS6"]
    rm_membs = ["SP1_2"]

    Ks, n2check = bld_subg_single_remove(G, rm_membs)

    for rm_memb, K in zip(rm_membs, Ks):
        draw_graph(
            G=K, filepath="{}/{}".format(f_out, rm_memb), scale=1.2, plt_show=True, plt_save=True
        )

    # Task #3: Joined Subgraphs
    if len(rm_membs) > 1:
        K_joined = bld_subg_multi(G, Ks, rm_membs, n2check)

        name = "_".join(rm_membs)
        draw_graph(
            G=K_joined,
            filepath="{}/_{}".format(f_out, name),
            scale=1.2,
            plt_show=True,
            plt_save=True,
        )

    # K_reduced = unroll_sequence(K)

    # draw_graph(
    #     G=K_reduced,
    #     pos_fixed=get_node_pos(K_reduced),
    #     filename="{}/_{}".format("P{}_graphs_out".format(phase_number), "test"),
    #     scale=1,
    #     plt_show=True,
    # )
