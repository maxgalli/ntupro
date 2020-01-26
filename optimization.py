from collections import Counter

from .booking import Unit
from .utils import Node

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
        paths (dict): dictionary where the keys are
            the names of the final actions performed
            (histograms and counts) and the values
            are lists containing the nodes in the
            path that needs to be followed to reach
            the action
    """
    def __init__(self, unit = None):
        if unit:
            logger.debug('%%%%%%%%%% Constructing graph from Unit')
            self.paths = dict()
            Node.__init__(self,
                unit.dataset.name,
                'dataset',
                unit.dataset)
            nodes = self.__nodes_from_unit(unit)
            for no_last, no_first in zip(
                    nodes[:-1], nodes[1:]):
                if isinstance(no_first, Node):
                    no_last.children.append(no_first)
                elif isinstance(no_first, list):
                    for action in no_first:
                        no_last.children.append(no_first)
                        self.paths[action.name] = nodes[:-1]
            logger.debug('%%%%%%%%%% Path for Unit: {}'.format(self.paths))
            self.children.append(nodes[0])

    def compute_nodes_priorities(self):
        """ Compute priorities for all the nodes in the
        graph. Useful for complex graphs during the
        swapping of the nodes in the optimization part.
        """
        priority = Counter()
        for path in self.paths.values():
            priority.update(path)
        for node, number in priority.items():
            if number == len(self.paths):
                for path in self.paths.values():
                    number += (len(path) - path.index(node))
                    priority[node] = number
        return priority

    def __nodes_from_unit(self, unit):
        nodes = list()
        last_node = list()
        for selection in unit.selections:
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
    def __init__(self, units):
        self.graphs = [
            Graph(unit) for unit in units]

    def add_graph(self, graph):
        self.graphs.append(graph)

    def add_graph_from_unit(self, unit):
        self.graphs.append(Graph(unit))

    def optimize(self, level = 2):
        if int(level) == 0:
            print('No optimization selected.')
        elif int(level) == 1:
            print('Level 1 optimization selected: merge datasets.')
            self.merge_datasets()
        elif int(level) >= 2:
            print('Level 2 optimization selected: merge datasets and selections.')
            self.merge_datasets()
            self.optimize_selections()
        else:
            print('Invalid level of optimization, default to FULL OPTIMIZED.')
            self.merge_datasets()
            self.optimize_selections()

    def merge_datasets(self):
        logger.debug('%%%%%%%%%% Merging datasets:')
        merged_graphs = list()
        for graph in self.graphs:
            if graph not in merged_graphs:
                merged_graphs.append(graph)
            else:
                for merged_graph in merged_graphs:
                    if merged_graph == graph:
                        merged_graph.paths.update(graph.paths)
                        for child in graph.children:
                            merged_graph.children.append(child)
        self.graphs = merged_graphs
        logger.debug('%%%%%%%%%% Merging datasets: DONE')
        self.print_merged_graphs()

    def optimize_selections(self):
        logger.debug('%%%%%%%%%% Optimizing selections:')
        for merged_graph in self.graphs:
            self._swap_children(merged_graph)
            self._merge_children(merged_graph)
        logger.debug('%%%%%%%%%% Optimizing selections: DONE')
        self.print_merged_graphs()

    def print_merged_graphs(self):
        print('Merged graphs:')
        for graph in self.graphs:
            print(graph)
            print('Paths: ', graph.paths)

    def _swap_children(self, node):
        priority = node.compute_nodes_priorities()
        logger.debug('Computed priorities {}'.format(priority))
        logger.debug('Swapping children in branches of root node {}'.format(
            node.__repr__()))
        for steps in node.paths.values():
            steps = steps.sort(key = lambda n: priority[n], reverse = True)
        node.children.clear()
        for steps in node.paths.values():
            for step in steps:
                step.children.clear()
            for no_last, no_first in zip(steps[:-1],
                    steps[1:]):
                no_last.children.append(no_first)
        node.children.extend([steps[0] for steps in node.paths.values()])
        logger.debug('DONE swapping for {}, new children: {}'.format(
            node.__repr__(), node.children))

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

