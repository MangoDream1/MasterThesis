from Aggregator.LinearAggregator import LinearAggregator
from Aggregator.GenericAggregator import GenericAggregator

import networkx as nx
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt


class DividedLinearAggregator(GenericAggregator):
    def __init__(self, transaction_cost=1, balance_diff_multiplier=1, **kwargs):
        super().__init__(transaction_cost=transaction_cost, 
                         balance_diff_multiplier=balance_diff_multiplier, 
                         **kwargs)

        self._iteration_points = []

    def iterate(self, set_generator, *generator_args):
        cons, cost = self.cost(self.matrix)
        self.log_data.append(np.array([cost, cons, cons + cost]))
        
        while True:
            old_cost = cost
            i = 0
            for nodes in set_generator(*generator_args):
                matrix = self.matrix[np.ix_(nodes, nodes)]
                
                agg = LinearAggregator()
                agg.set_init_variables(matrix, None)
                agg.iterate()
                
                self.matrix[np.ix_(nodes, nodes)] = agg.matrix

                if i % 10:
                    cons, cost = self.cost(self.matrix)
                    self.log_data.append(np.array([cost, cons, cons + cost]))
                i += 1

            self.network = nx.from_scipy_sparse_matrix(self.matrix, create_using=nx.DiGraph())
            self._iteration_points.append(len(self.log_data))

            if old_cost == cost:
                break
            
    def get_triangles(self):
        # TODO: with recursion
        network = self.network.to_undirected()

        for node in network.nodes:
            for x in network.neighbors(node):
                for y in network.neighbors(x):
                    if network.adj[y].get(node, None):
                        yield list({node, x, y}) # FIXME: always duplicate

    def get_connected(self, max_length):
        network = self.network.to_undirected()
        for xnode, ynode in combinations(network.nodes, 2):
            for path in nx.all_simple_paths(network, xnode, ynode, max_length):
                yield path

    def all_combinations(self, size):
        network = self.network.to_undirected()        
        return combinations(network.nodes, size)

    def plot_log_data(self):
        super().plot_log_data(False)

        plots = [131, 132, 133]

        for plot in plots:
            for xc in self._iteration_points:
                plt.subplot(plot).axvline(x=xc, color='red', label=plot)

        plt.show()

    # TODO: think of better ways than triangles; cliques to large; somewhere inbetween 
    #https://en.wikipedia.org/wiki/Clique_problem
    #https://en.wikipedia.org/wiki/Strongly_connected_component