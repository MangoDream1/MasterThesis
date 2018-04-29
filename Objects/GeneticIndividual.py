from constants.constants import MATRIX_FORMAT


class GeneticIndividual():
    def __init__(self, matrix, cost_func):
        self.cost_func = cost_func
        self.matrix = matrix.copy().asformat(MATRIX_FORMAT)

        self.update()

    def update(self):
        cons_violation, cost = self.cost_func(self.matrix)

        self.cons_violation = cons_violation
        self.cost = cost
        self.combined_cost = cost + cons_violation
        self.valid = cons_violation == 0
        self.crowding_dist = 0