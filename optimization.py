from copy import deepcopy
from collections import Counter

from .booking import Unit
from .utils import Node
from .utils import PrintedNode
from .utils import drawTree2

import logging
logger = logging.getLogger(__name__)



class Graph(Node):
    """
    A Graph is itself a node and every node has other nodes as children.
    Due to the way it is constructed, the root node will always be of
    kind 'dataset'.

    Args:
        unit (Unit): unit object from which a graph
            in its basic form is generated
        split_selections (Bool): boolean value
            indicating if we want to split the selections
            into minimal units

    Attributes:
        unit (Unit): unit object from which a graph
            in its basic form is generated
        split_selections (Bool): boolean value
            indicating if we want to split the selections
            into minimal units
    """
    def __init__(self, unit, split_selections = False):
        logger.debug('%%%%%%%%%% Constructing graph from Unit')
        self.split_selections = split_selections
        Node.__init__(self,
            unit.dataset.name,
            'dataset',
            unit.dataset)
        nodes = self.__nodes_from_unit(unit)
        if len(nodes) > 1:
            for no_last, no_first in zip(
                    nodes[:-1], nodes[1:]):
                if isinstance(no_first, Node):
                    no_last.children.append(no_first)
                elif isinstance(no_first, list):
                    for action in no_first:
                        no_last.children.append(action)
            self.children.append(nodes[0])
        else:
            # no-selections case: the only element of nodes is the
            # list of actions
            self.children.extend(nodes[0])

    def __nodes_from_unit(self, unit):
        nodes = list()
        last_node = list()
        for selection in unit.selections:
            if self.split_selections:
                sub_selections = selection.split()
                for sub_selection in sub_selections:
                    nodes.append(
                        Node(
                            sub_selection.name,
                            'selection',
                            sub_selection))
            else:
                nodes.append(
                    Node(
                        selection.name,
                        'selection',
                        selection))
        for action in unit.actions:
            last_node.append(
                Node(
                    action.name,
                    'action',
                    action))
        nodes.append(last_node)
        return nodes


class GraphManager:
    """
    Manager for Graph-type objects, with the main function of
    optimize/merge them with the 'optimize' function.

    Args:
        units (list): List of Unit objects used to
            fill the 'graphs' attribute

    Attributes:
        graphs (list): List of Graph objects that at some point
            will be merged and optimized
    """
    def __init__(self, units, split_selections = False):
        self.graphs = [
            Graph(unit, split_selections) for unit in units]

    def add_graph(self, graph):
        self.graphs.append(graph)

    def add_graph_from_unit(self, unit):
        self.graphs.append(Graph(unit))

    def optimize(self, level = 2):
        if int(level) == 0:
            logger.debug('No optimization selected.')
        elif int(level) == 1:
            logger.debug('Level 1 optimization selected: merge datasets.')
            self.merge_datasets()
        elif int(level) >= 2:
            logger.debug('Level 2 optimization selected: merge datasets and selections.')
            self.merge_datasets()
            self.optimize_selections()
        else:
            logger.debug('Invalid level of optimization, default to FULL OPTIMIZED.')
            self.merge_datasets()
            self.optimize_selections()
        logger.debug('Merged graphs:\n{}'.format(self.get_pretty_printed_merged_graphs()))

    def merge_datasets(self):
        logger.debug('%%%%%%%%%% Merging datasets:')
        merged_graphs = list()
        for graph in self.graphs:
            if graph not in merged_graphs:
                merged_graphs.append(graph)
            else:
                for merged_graph in merged_graphs:
                    if merged_graph == graph:
                        for child in graph.children:
                            merged_graph.children.append(child)
        self.graphs = merged_graphs
        logger.debug('%%%%%%%%%% Merging datasets: DONE')

    def optimize_selections(self):
        logger.debug('%%%%%%%%%% Optimizing selections:')
        for merged_graph in self.graphs:
            self._merge_children(merged_graph)
        logger.debug('%%%%%%%%%% Optimizing selections: DONE')

    def get_pretty_printed_merged_graphs(self):
        def call_node_rec(nd):
            return PrintedNode(nd.__repr__())([call_node_rec(child) for child in nd.children])
        fancy_trees = [call_node_rec(graph) for graph in self.graphs]
        return '\n\n'.join([drawTree2(False)(False)(t) for t in fancy_trees])

    def _merge_children(self, node):
        '''For every node, loops through the children
        and merges the ones that are equal, by appending
        the children of the new spotted ones to the
        children of the first spotted.
        '''
        merged_children = list()
        for child in node.children:
            if child not in merged_children:
                merged_children.append(child)
            else:
                merged_children[merged_children.index(
                    child)].children.extend(
                        child.children)
        node.children = merged_children
        for child in node.children:
            self._merge_children(child)
