from constants.constants import *

from collections import defaultdict
import networkx as nx
import numpy as np
import scipy as sc
from random import *


class GenericAggregator:
    def __init__(self, transaction_cost=100, balance_diff_multiplier=10):
        self._calculate_end_balances = lambda matrix: sum(matrix - matrix.T).toarray()

        self.transaction_cost = transaction_cost
        self.balance_diff_multiplier = balance_diff_multiplier

    def set_init_variables(self, matrix, network):
        self.matrix = matrix.asformat(MATRIX_FORMAT)
        self.network = network
        self._get_actors()
        self._get_goal_balance()

    def cost(self, matrix):
        """
        Calculates the cost of a block
        :param matrix: the graph matrix
        :param goal_balance: the balance that is being compared to
        :return: constraint violation, cost tuple
        """

        diff = np.absolute(self._calculate_end_balances(matrix) - self.goal_balance).sum()
        n_transactions = matrix.count_nonzero()

        return diff * self.balance_diff_multiplier, n_transactions * self.transaction_cost

    def mutate(self, matrix):
        """
        Override method for mutation of matrix
        """
        pass
    
    def step(self):
        """
        Override method for algorithm step
        """
        pass

    def _get_actors(self):
        """
        Creates an nested dictionary of the actor location in the end balance array
        :return: 
        """

        self._actors = {}        
        actors = []

        for to, fr in self.network.edges():
                actors.extend([to, fr])

        for i, a in enumerate(set(actors)):
            self._actors[a] = i

    def _get_goal_balance(self):
        """
        Calculates the end balance for each actor in each block
        :return:
        """
        self.goal_balance = self._calculate_end_balances(self.matrix)
        self.abs_max = np.absolute(self.goal_balance).max()