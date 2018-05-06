from Aggregator.LinearAggregator import LinearAggregator
from Aggregator.GenericAggregator import GenericAggregator

import networkx as nx
import numpy as np

class DividedLinearAggregator(GenericAggregator):
    def __init__(self, transaction_cost=1, balance_diff_multiplier=1, **kwargs):
        super().__init__(transaction_cost=transaction_cost, 
                         balance_diff_multiplier=balance_diff_multiplier, 
                         **kwargs)

    def iterate(self, set_generator):
        cons, cost = self.cost(self.matrix)
        self.log_data.append(np.array([cost, cons, cons + cost]))

        while True:
            old_cost = cost
            for nodes in set_generator:
                matrix = self.matrix[np.ix_(nodes, nodes)]
                
                agg = LinearAggregator()
                agg.set_init_variables(matrix, None)
                agg.iterate()
                
                self.matrix[np.ix_(nodes, nodes)] = agg.matrix

                cons, cost = self.cost(self.matrix)
                self.log_data.append(np.array([cost, cons, cons + cost]))

            if old_cost == cost:
                break
            
    def get_triangles(self):
        for node in self.network.to_undirected().nodes:
            for x in self.network.neighbors(node):
                for y in self.network.neighbors(x):
                    if self.network.adj[y].get(node, None):
                        yield list({node, x, y}) # FIXME: always duplicate

    # def get_connected(self, length):
        


    # TODO: think of better ways than triangles; cliques to large; somewhere inbetween 
    #https://en.wikipedia.org/wiki/Clique_problem
    #https://en.wikipedia.org/wiki/Strongly_connected_component