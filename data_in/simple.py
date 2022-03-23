data_in = {
    "name": "SimpleStructure",
    "output_vid": "outputs/SimpleStructure.gif",
    "backtrack": "peterson",
    "n_max_steps": 100,
    "n_gradient_steps": 100,
    #
    "vertices": {
        0: (0, 0),
        1: (5.5, 0),
        2: (4.5, 7),
    },
    "edges": {
        0: (0, 1),
        1: (0, 2),
        2: (1, 2),
    },
    "edge_lengths": [],
    "rigid_edge": [0],
    #
    "plotting_features1": {"n_color": "#afcdfa", "e_color": ["k"], "width": 2},
    "plotting_features2": {
        "n_color": "#ffbfd7",
        "e_color": "r",
        "width": 2,
    },
    #
    "initial_conditions": {
        0: {
            0: (0, 0),
            1: (5.5, 0),
            2: (1, 1.1),
        },
        1: {
            0: (0, 0),
            1: (5.5, 0),
            2: (6, -0.2),
        },
    },
}
