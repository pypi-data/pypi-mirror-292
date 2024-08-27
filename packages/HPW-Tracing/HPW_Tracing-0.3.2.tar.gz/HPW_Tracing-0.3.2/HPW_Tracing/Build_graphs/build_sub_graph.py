import networkx
import networkx as nx
import typing

def create_abstract_graph(original_graph: networkx.DiGraph, subset_nodes: typing.List[str])-> networkx.DiGraph:
    """
    This fucntion takes a directed graph and a subset of nodes and returns an abstract graph with only the subset of nodes
    :param original_graph:
    :param subset_nodes:
    :return:
    """

    # Initialize an empty directed graph for the abstract graph
    abstract_graph = nx.DiGraph()

    # Add the subset of nodes to the abstract graph along with their attributes
    for node in subset_nodes:
        if node in original_graph.nodes():
            abstract_graph.add_node(node, **original_graph.nodes[node])

    # Add edges based on the existence of direct paths in the original graph
    for source in subset_nodes:
        for target in subset_nodes:
            if source != target:
                try:
                    # Check the shortest path between source and target
                    shortest_path = nx.shortest_path(original_graph, source, target)
                    # remove the element in the path if it is not in the subset
                    shortest_path = [node for node in shortest_path if node in subset_nodes]
                    # Ensure the shortest path contains only source and target
                    if len(shortest_path) == 2:
                        abstract_graph.add_edge(source, target)
                except nx.NetworkXNoPath:
                    # If there's no path, ignore and move to the next pair
                    continue

    # if the abstract_graph is empty, raise an error
    if len(abstract_graph.nodes()) == 0:
        raise ValueError('None of the nodes belong to the original graph')

    return abstract_graph