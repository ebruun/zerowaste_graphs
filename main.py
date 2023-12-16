from msilib import sequence
from src.build import (
    bld_g_full,
    bld_subg_single_remove,
    bld_subg_multi_remove,
    bld_sequence,
)

from src.drawing import draw_graph


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

    # Task #2: Member Removal Sub-graphs
    rm_membs = list(G.nodes())
    # rm_membs = ["ES10", "EP1_2", "NP1_1", "ER2"] #paper figure, single
    # rm_membs = ["WS3", "WP1_2"] #paper figure, joined
    # rm_membs = ["SS1", "WS9", "WP1_3", "SS6"]
    # rm_membs = ["WS9", "SS1"]
    # rm_membs = ["SS3", "SS1"]

    Ks = bld_subg_single_remove(G, rm_membs)

    for rm_memb, K in zip(rm_membs, Ks):
        if K.number_of_nodes() > 1:
            draw_graph(
                G=K,
                filepath="{}/{}".format(f_out, rm_memb),
                scale=1.2,
                plt_show=False,
                plt_save=True,
            )

    # Joined Subgraphs
    # if len(rm_membs) > 1:
    #     K_joined = bld_subg_multi_remove(G, Ks, rm_membs)

    #     name = "_".join(rm_membs)
    #     draw_graph(
    #         G=K_joined,
    #         filepath="{}/_{}".format(f_out, name),
    #         scale=1.2,
    #         plt_show=True,
    #         plt_save=True,
    #     )

    # Task #3: Sequence Generate
    # K_reduced_list, members = bld_sequence(K_joined, rm_membs)

    # for i, (K_reduced, member) in enumerate(zip(K_reduced_list, members)):
    #     draw_graph(
    #         G=K_reduced,
    #         filepath="{}/_step{}".format(f_out, i + 1),
    #         scale=1.2,
    #         plt_show=True,
    #         plt_save=True,
    #         plt_text=member,
    #     )
