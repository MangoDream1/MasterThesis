from Aggregator.LinearAggregator import LinearAggregator
from Aggregator.GenericAggregator import GenericAggregator

import networkx as nx
import numpy as np
from itertools import combinations
import matplotlib.pyplot as plt
from collections import deque

# TODO: parallize process // subgraphs
class DividedLinearAggregator(GenericAggregator):
    def __init__(self, non_improvement=50, transaction_cost=1, 
                 balance_diff_multiplier=1, **kwargs):
        super().__init__(transaction_cost=transaction_cost, 
                         balance_diff_multiplier=balance_diff_multiplier, 
                         **kwargs)

        self._iteration_points = []
        self._end_iteration_points = []
        self._non_improvement_points = []
        self._cons_violation_points = []
        
        self._cons_violation_size = []

        self.non_improvement = non_improvement
        self.linear_aggregator_kwargs = {}

    def iterate(self, set_generator, *generator_args):
        cons, cost = self.cost(self.matrix)
        self.log_data.append(np.array([cost, cons, cons + cost]))
        
        non_improvement = 0
        log_data_length = len(self.log_data)        
        while True:
            old_cost = cost
            i = 0
            for nodes in set_generator(*generator_args):
                matrix = self.matrix[np.ix_(nodes, nodes)]
                
                agg = LinearAggregator()
                agg.set_init_variables(matrix, None)
                result = agg.iterate(**self.linear_aggregator_kwargs)
                
                if result == float("inf"): # not solvable
                    continue

                part_cost = agg.cost(agg.matrix)
                if part_cost[0] == 0 and part_cost[1] <= matrix.count_nonzero():
                    self.matrix[np.ix_(nodes,nodes)] = agg.matrix
                else:
                    self._cons_violation_points.append(log_data_length)
                    self._cons_violation_size.append(part_cost[0])

                if i % 10:
                    cons, cost = self.cost(self.matrix)
                    self.log_data.append(np.array([cost, cons, cons + cost]))
                    log_data_length += 1
                i += 1

            self.network = nx.from_scipy_sparse_matrix(self.matrix, create_using=nx.DiGraph())
            self._iteration_points.append(log_data_length)            
            cons, cost = self.cost(self.matrix)

            if old_cost == cost:
                non_improvement += 1
            else:
                non_improvement = 0
            
            if non_improvement == self.non_improvement:
                break
            
            if non_improvement == 1:
                self._non_improvement_points.append(log_data_length)
    
        self._end_iteration_points.append(log_data_length)
            
    def get_loop(self, size, found_length=10): #TODO: experiment with found_length
        network = self.network.to_undirected()        
        found = deque([], found_length)

        def recursion(node, start_node, loop):        
            if len(loop) < size:    
                for neighbor in network.neighbors(node):
                    if neighbor not in loop:
                        yield from recursion(neighbor, start_node, loop + [neighbor])
                    
            elif network.adj[node].get(start_node, None):
                sorted_loop = sorted(loop)

                if sorted_loop not in found:
                    found.append(sorted_loop)
                    yield sorted_loop      

        for node in network.nodes:
            yield from recursion(node, node, [node])


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

        cons_violation = np.zeros(len(self.log_data)) 
        cons_violation[self._cons_violation_points] = self._cons_violation_size

        plt.subplot(132).plot(cons_violation)

        plots = [131, 132, 133]

        for plot in plots:
            for xc in self._iteration_points:
                plt.subplot(plot).axvline(x=xc, color='red', label=plot, ymax=0.03)

            for xc in self._end_iteration_points:
                plt.subplot(plot).axvline(x=xc, color='black', label=plot, ymax=1)   

            for xc in self._non_improvement_points:
                plt.subplot(plot).axvline(x=xc, color='green', label=plot, ymax=0.04)

            for xc in self._cons_violation_points:
                plt.subplot(plot).axvline(x=xc, color='purple', label=plot, ymax=0.02)             

        plt.show()

    # TODO: think of better ways than triangles; cliques to large; somewhere inbetween 
    #https://en.wikipedia.org/wiki/Clique_problem
    #https://en.wikipedia.org/wiki/Strongly_connected_component