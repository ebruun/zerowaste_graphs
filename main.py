# from msilib import sequence
from src.build import (
    bld_g_full,
    bld_g_sub,
    bld_subg_single_remove,
    bld_subg_multi_remove,
    bld_sequence,
)

from src.drawing import draw_graph


if __name__ == "__main__":
    phase_number = "3"
    f_in = "P{}_data_in".format(phase_number)
    f_out = "P{}_graphs_out".format(phase_number)

    # Task #1: Building Overall Support Hierarchy
    G = bld_g_full(f_in)

    draw_graph(
        G=G,
        filepath="{}/{}".format(f_out, "__full_structure.png"),
        scale=1,
        plt_show=False,
        plt_save=False,
    )

    if phase_number == "3":
        # For Phase 3 figures
        steps = 25

        Ks = bld_g_sub(G, f_in, steps)

        for K in Ks:
            i = K.graph["step"]
            name = f"phase3_subset_{i}.png"
            draw_graph(
                G=K,
                filepath="{}/{}".format(f_out, name),
                scale=1.2,
                plt_show=False,
                plt_save=True,
                plt_text=True,
            )
    else:
        # Task #2: Member Removal Sub-graphs
        # rm_membs = list(G.nodes())
        # rm_membs = ["ES10", "EP1_2", "NP1_1", "ER2"]  # Paper figure, single
        # rm_membs = ["WP1_2", "WS3"]  # Paper figure, joined
        # rm_membs = ["SS1"]  # Phase 1
        # rm_membs = ["WS9", "SS1"]  # Phase 1
        # rm_membs = ["SS3", "SS1"]  # Phase 1
        # rm_membs = ["SP1_2", "SP1_3", "SP1_4"]  # Phase 2a_1
        # rm_membs = ["SP1_4", "ES10", "SP1_2", "SP1_3"]  # Phase 2a_2
        # rm_membs = ["SP1_4", "ES10", "SP1_2", "SP1_3", "RG1_6"]  # Phase 2a_3
        rm_membs = ["SP1_2", "SP1_3", "RG1_6"]  # Phase 2b

        Ks = bld_subg_single_remove(G, rm_membs)

        for rm_memb, K in zip(rm_membs, Ks):
            if K.number_of_nodes() > 1:
                draw_graph(
                    G=K,
                    filepath="{}/{}".format(f_out, rm_memb),
                    scale=1.2,
                    plt_show=False,
                    plt_save=False,
                    plt_text=False,
                )

        # Joined Subgraphs
        name = "_".join(rm_membs)
        if len(rm_membs) > 1:
            K_joined = bld_subg_multi_remove(G, Ks, rm_membs)

            draw_graph(
                G=K_joined,
                filepath="{}/_{}".format(f_out, name),
                scale=1.2,
                plt_show=True,
                plt_save=True,
                plt_text=True,
            )
        else:
            K_joined = Ks[0]

        # Task #3: Sequence Generate
        K_reduced_list, members = bld_sequence(K_joined, rm_membs)

        for K_reduced in K_reduced_list:
            i = K_reduced.graph["step"]
            draw_graph(
                G=K_reduced,
                filepath="{}/_{}_STEP{}".format(f_out, name, i),
                scale=1.2,
                plt_show=True,
                plt_save=True,
                plt_text=True,
            )
