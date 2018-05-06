from constants.constants import *

from collections import defaultdict
import networkx as nx
import numpy as np
import scipy as sc
from random import *
import matplotlib.pyplot as plt


class GenericAggregator:
    def __init__(self, mutation_rate=0.1, deviations_divider=3, 
                 transaction_cost=100, balance_diff_multiplier=10):
        self._calculate_end_balances = lambda matrix: sum(matrix - matrix.T).toarray()[0]

        self.transaction_cost = transaction_cost
        self.balance_diff_multiplier = balance_diff_multiplier

        self.mutation_rate = mutation_rate
        self.deviations_divider = deviations_divider

        self.log_data = []
    
    def set_init_variables(self, matrix, network):
        self.matrix = matrix.asformat(MATRIX_FORMAT)
        self.start_matrix = matrix.asformat(MATRIX_FORMAT)
        self.network = network
        self._get_actors()
        self._get_goal_balance()

        self.correction_matrix = np.ones(self.matrix.shape)
        np.fill_diagonal(self.correction_matrix, 0.)

    def corrections(self, matrix):
        matrix = matrix.multiply(
            self.correction_matrix).asformat(MATRIX_FORMAT)

        matrix[matrix < 0] = 0
        matrix[matrix > self.abs_max] = self.abs_max

        return matrix.astype(int)

    def cost(self, matrix):
        """
        Calculates the cost of a block
        :param matrix: the graph matrix
        :param goal_balance: the balance that is being compared to
        :return: (constraint violation, cost) tuple
        """

        diff = np.square(self._calculate_end_balances(matrix) - self.goal_balance).sum()
        cons = matrix[matrix < 0].sum() * -1

        n_transactions = matrix.count_nonzero()

        return (cons + diff) * self.balance_diff_multiplier, n_transactions * self.transaction_cost

    def mutate(self, matrix):
        #     selection = sc.sparse.rand(*matrix.shape, mutation_rate) > 0 # look if always 10% then problem
        #     amounts = np.random.normal(0, abs_max/deviations_divider, len(selection.data)).astype(int)

        selection = np.random.random(matrix.shape) < self.mutation_rate
        amounts = np.random.normal(0, self.abs_max/self.deviations_divider,
                                   len(selection[selection == True])).astype(int)

        matrix[selection] += amounts

        return matrix
    
    def step(self):
        """
        Override method for algorithm step
        """
        pass

    def iterate(self):
        """
        Override method for algorithm iteration
        """
        pass

    def _get_actors(self):
        """
        Creates an nested dictionary of the actor location in the end balance array
        :return: 
        """

        self.actor_to_index = {}        
        self.index_to_actor = {}

        for i, node in enumerate(self.network.nodes()):
            self.actor_to_index[node] = i
            self.index_to_actor[i] = node

    def _get_goal_balance(self):
        """
        Calculates the end balance for each actor in each block
        :return:
        """
        self.goal_balance = self._calculate_end_balances(self.matrix)
        self.abs_max = np.abs(self.goal_balance).max()

    def plot_log_data(self):
        plt.figure(1, figsize=(20, 5))

        plt.subplot(131).title.set_text("cost")
        plt.plot(np.array(self.log_data)[:, 0])

        plt.subplot(132).title.set_text("cons_violation")
        plt.plot(np.array(self.log_data)[:, 1])

        plt.subplot(133).title.set_text("combined_cost")
        plt.plot(np.array(self.log_data)[:, 2])

        plt.show()

    def plot_network(self):
        self.network = nx.from_scipy_sparse_matrix(self.matrix, create_using=nx.DiGraph())

        nx.draw(self.network, with_labels=True)
        plt.show()        
