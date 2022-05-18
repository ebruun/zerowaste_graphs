from src.build import build_full_graph, build_member_subgraph


if __name__ == "__main__":

    G = build_full_graph(
        folder="data_in",
        filename="_full_structure.png",
        scale=1,
        draw=True,
        show=False,
    )

    # remove_members = G.nodes()

    remove_members = ["SP1_1"]
    K1 = build_member_subgraph(
        G=G,
        remove_members=remove_members,
        scale=1.2,
        draw=True,
        show=False,
    )

    # remove_members = ["WS9"]
    # K2 = build_member_subgraph(G=G, remove_members=remove_members, draw=False, show=False)

    # K_combo = nx.compose(K2,K1)

    # draw_graph(
    #     G=K_combo,
    #     pos_fixed=get_node_pos(K_combo),
    #     filename="graphs_out/{}".format("__test"),
    #     scale=1,
    #     plt_show=True,
    # )
