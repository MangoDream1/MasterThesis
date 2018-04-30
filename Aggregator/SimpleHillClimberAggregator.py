import scipy as sc
import numpy as np
import networkx as nx
from random import random

from constants.constants import MATRIX_FORMAT
from Aggregator.GenericAggregator import GenericAggregator

class SimpleHillClimber(GenericAggregator):
    def __init__(self, non_improvement=500, **kwargs):
        super().__init__(**kwargs)

        self.non_improvement = non_improvement

    def iterate(self):
        cons_violation, cost  = self.cost(self.matrix)
        combined_cost = cost + cons_violation

        self.log_data.append(np.array([cost, cons_violation, combined_cost]))
        non_improvement = 0
        
        while non_improvement <= self.non_improvement and combined_cost != 0:
            old_matrix = self.matrix.copy()
            self.matrix = self.mutate(self.matrix)

            cons_violation, cost = self.cost(self.matrix)
            combined_cost2 = cons_violation + cost

            if combined_cost2 >= combined_cost:
                non_improvement += 1
                self.matrix = old_matrix
            else:
                non_improvement = 0
                combined_cost = combined_cost2
            
                self.log_data.append(np.array([cost, cons_violation, combined_cost2]))

        self.matrix = self.corrections(self.matrix)
        self.network = nx.from_scipy_sparse_matrix(self.matrix, create_using=nx.DiGraph())

    def random_start(self):
        self.matrix = sc.sparse.random(*self.matrix.shape, random(), MATRIX_FORMAT)
        self.matrix *= self.abs_max
        self.matrix = self.corrections(self.matrix)