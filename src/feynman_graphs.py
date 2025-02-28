from base_feynman_graph import FeynmanGraph
from typing import List
# from pandas import DataFrame
from particles import ParticleRegistry, Particle
# import os.path as osp

# CURRENT_DIR = osp.dirname(osp.abspath(__file__))
# DATASETPATH = osp.join(osp.dirname(CURRENT_DIR), "data")
# RAW_DIR = f"{DATASETPATH}/raw"


# ## Diagram structures
# * s-channel
# * t-channel
# * u-channel
#
# Need to think if i want these to be instances of the FeynmanGraph class or inherited from...
# Also need the specific diagrams to be either an instance or inherited from a classs


class S_Channel(FeynmanGraph):
    def __init__(self):
        super().__init__()
        # Add edges
        edges = [(1, 3), (2, 3), (3, 4), (4, 5), (4, 6)]
        self.add_edges(edges)

        initial = [1, 0, 0]
        virtual = [0, 1, 0]
        final = [0, 0, 1]
        # Bad idea to have the global node with a different context to the 1-hot
        # encodings of the individual nodes. Commenting out for now
        # global_node = [alpha_QED, alpha_W, alpha_S]

        self.node_feat = {
            1: initial,
            2: initial,
            3: virtual,
            4: virtual,
            5: final,
            6: final,
        }


class T_Channel(FeynmanGraph):
    def __init__(self):
        super().__init__()
        # Add edges
        edges = [(1, 3), (2, 4), (3, 4), (3, 5), (4, 6)]
        self.add_edges(edges)

        initial = [1, 0, 0]
        virtual = [0, 1, 0]
        final = [0, 0, 1]

        self.node_feat = {
            1: initial,
            2: initial,
            3: virtual,
            4: virtual,
            5: final,
            6: final,
        }


class U_Channel(FeynmanGraph):
    def __init__(self):
        super().__init__()
        # Add edges
        edges = [(1, 3), (2, 4), (3, 4), (3, 6), (4, 5)]
        self.add_edges(edges)

        initial = [1, 0, 0]
        virtual = [0, 1, 0]
        final = [0, 0, 1]
        # Bad idea to have the global node with a different context to the 1-hot
        # encodings of the individual nodes. Commenting out for now
        # global_node = [alpha_QED, alpha_W, alpha_S]

        self.node_feat = {
            1: initial,
            2: virtual,
            3: final,
            4: initial,
            5: virtual,
            6: final,
        }


# ## Feynman Diagram builder
#
# A function to create a list of all possible diagrams
#
# 1.   Takes in initial and final particle states
# 2.   Iterates over diagram structures (s,t,u for tree level)
# 3.   Iterates over vertices
# 4.   Removes diagrams that don't follow conservation rules
#
# ---
#
# ## Create Tree-level QED Dataset
#
# We start with simple electron positron to muon antimuon QED tree level scattering. This removes the need for the t-channel diagram. And we only need to consider the s-channel diagram.
#
# The structure is to create a list for each of the features.
#
# Then create a list of lists to represent the data for a singular graph
#
# Then create a stacked list of lists of lists to represent the full dataset which then gets passed to pandas.dataframe
#
# As a numpy array, this will be a 2D array (num_graphs, num_feature_type) with the objects as lists.
#
# I first give the 4 non-zero matrix elements and then include two that are zero.

def build_tree_diagrams_QED(
    initial_1,
    initial_2,
    final_5,
    final_6,
    channel: FeynmanGraph,
    global_connect: bool,
)-> List[FeynmanGraph]:
    """
    Function to make return all possbile diagrams with given initial and final states.

    Behaviour
    ---
    Creates the graph base, by assigning the edge features.
    Cycles through possible propagators and checks if valid
    Returns list of all allowed ones

    Returns
    ---
    Returns a list allowed graphs, which consist of Feyn_vertex, edge_index and edge_feat
    Changes: should allow feynman diagrams with False to be returned but force them to have matrix element 0; exclude certain vertices e.g. connecting electron to muon
    """

    graph: FeynmanGraph = channel()

    # TODO - check to see if process is kinematically allowed by conserving energy, helicity and momentum (need to add)
    edge_feats = {
        1: initial_1,
        2: initial_2,
        5: final_5,
        6: final_6,
    }
    graph.add_edge_feat(edge_feats)

    # create a list of allowed edges to insert between virtual nodes
    graphs = []

    # look for virtual nodes connected to virtual nodes
    for e in graph.edge_index:
        if e[0] == [0,1,0] and e[1] == [0,1,0]:
            graph.edge_feat[e] = ParticleRegistry.get_particle_class("photon")

    # cycle through edge_position
    """
    look at edge positions, take all the indices in edge positions
    make lists for each 
    """

    # Connect the global node and make the graph undirected
    if global_connect is True:
        graph.connect_global_node()

    graph.make_edges_undirected()

    # make the features undirected
    graphs.append(graph)

    return graphs


def diagram_builder_gluon(
    initial_0,
    initial_1,
    final_4,
    final_5,
    channel,
    global_connect: bool,
) -> List[FeynmanGraph]:
    """
    Similar function to above. Returns all possbile diagrams with initial and final states given with a gluon propagator.

    Returns
    ---
    Returns a list allowed graphs, which consist of Feyn_vertex, edge_index and edge_feat
    Changes: should allow feynman diagrams with False to be returned but force them to have matrix element 0; exclude certain vertices e.g. connecting electron to muon

    FIXME - Old function, replaced by build_tree_diagrams
    """
    Feyn_vertex, adj_class = channel
    num_edges = adj_class.graph_size()
    edge_index = adj_class.get_list()
    # check to see if process is kinematically allowed by conserving energy, helicity and momentum (need to add)

    # Given edge features
    incoming_0 = initial_0.get_feat()
    incoming_1 = initial_1.get_feat()
    outgoing_4 = final_4.get_feat()
    outgoing_5 = final_5.get_feat()

    # make empty edge feature list for directed graph
    edge_feat = [0] * num_edges

    # assign initial and final edge feats. NEED TO CHANGE THIS TO SEARCH FOR INIT AND FINAL NODES AS THE INDICES
    edge_feat[0] = incoming_0
    edge_feat[1] = incoming_1
    edge_feat[-2] = outgoing_4
    edge_feat[-1] = outgoing_5

    # create a list of allowed edges to insert between virtual nodes
    graphs = []
    propagators = []
    # edge_position = []
    for i in range(len(edge_index[0])):  # len(edge_index[0] is the number of edges)
        # look for virtual nodes connected to virtual nodes
        if Feyn_vertex[edge_index[0][i]] == [0, 1, 0] and Feyn_vertex[
            edge_index[1][i]
        ] == [0, 1, 0]:  # 1-hot encoding for virtual nodes
            # cycle through list of bosons (just photons for now)
            edge_feat[i] = ParticleRegistry.get_particle_class("gluon_rbbar").get_feat()
            # if vertex_check(edge_index[0][i], edge_feat, edge_index):
            #     propagators.append(edge_feat[i])
            #     edge_position.append(i)
            if not propagators:  # checks to see if the list is empty
                return []

    # cycle through edge_position
    """
    look at edge positions, take all the indices in edge positions
    make lists for each 
    """

    # Connect the global node and make the graph undirected
    if global_connect is True:
        adj_class.connect_global_node()

        # add global node edge features
        num_nodes = len(Feyn_vertex)  # including super node
        for i in range(1, num_nodes):
            global_edge_features = [0] * len(edge_feat[0])
            edge_feat.append(global_edge_features)

    adj_class.undirected()
    edge_index = adj_class.get_list()

    # make the features undirected
    edge_feat += edge_feat
    graphs.append([Feyn_vertex, edge_index, edge_feat])

    return graphs[0]

def build_tree_diagrams(
    initial_1,
    initial_2,
    final_5,
    final_6,
    channel: FeynmanGraph,
    propagators: list["Particle"] = [ParticleRegistry.get_particle_class("photon")()],
    global_connect: bool = True,
)-> List[FeynmanGraph]:

    # TODO - check to see if process is kinematically allowed by conserving energy, helicity and momentum (need to add). Maybe to vertex check, or maybe to a separate function called kinematic_check()
    # FIXME - This only works for the T-Channel, because the edge features are hard coded. Need to make it work for all channels!!
    edge_feats = {
        (1,3): initial_1,
        (2,4): initial_2,
        (3,5): final_5,
        (4,6): final_6,
    }

    # create a list of allowed edges to insert between virtual nodes
    graphs = []

    graph: FeynmanGraph = channel()
    graph.add_edge_feat(edge_feats)

    # look for virtual nodes connected to virtual nodes
    for e in channel().edge_index:
        if graph._node_feat_dict[e[0]] == [0,1,0] and graph._node_feat_dict[e[1]] == [0,1,0]:
            for p in propagators:
                graph._edge_feat_dict[e] = p.get_features()
                if graph.vertex_check():
                    graphs.append(graph)
                    graph = channel()
                    graph.add_edge_feat(edge_feats)

    return graphs