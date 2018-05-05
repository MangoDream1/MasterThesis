from Aggregator.GenericAggregator import GenericAggregator
from cvxpy import Problem, Minimize, sum_entries, Variable, Bool
import numpy as np
import networkx as nx


class LinearAggregator(GenericAggregator):
    def __init__(self, solver="ECOS_BB", **kwargs):
        super().__init__(**kwargs)

        self.solver = solver
        self._calculate_end_balances = lambda matrix: sum_entries(matrix.T - matrix, axis=0)

    def set_init_variables(self, matrix, network):
        super().set_init_variables(matrix, network)

        self.problem_matrix = Variable(*matrix.shape)
        self.count_matrix = Bool(*matrix.shape)

        self.constraints = [
            self._calculate_end_balances(self.problem_matrix) == self.goal_balance,
            self.problem_matrix >= 0,
            self.problem_matrix <= self.abs_max * self.count_matrix
        ]

        self.problem = Problem(Minimize(sum_entries(self.count_matrix)), self.constraints)

    def corrections(self):
        pass
    
    def cost(self, matrix):
        pass
    
    def mutate(self, matrix):
        pass
    
    def step(self):
        pass

    def iterate(self, **kwargs):
        result = self.problem.solve(self.solver, **kwargs)

        if result == float("inf"):
            print("Not solvable")
            return result

        self.matrix = np.round(self.problem_matrix.value, 2)
        self.network = nx.from_numpy_matrix(self.matrix, create_using=nx.DiGraph())

        return result

    def _get_goal_balance(self):
        """
        Calculates the end balance for each actor in each block
        :return:
        """
        self.goal_balance = self._calculate_end_balances(self.matrix)
        self.abs_max = np.abs(self.goal_balance.value).max()

    def plot_log_data(self):
        pass