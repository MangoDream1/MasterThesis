from collections import defaultdict
from random import *

import matplotlib.pyplot as plt
import numpy as np
import scipy as sc

from Aggregator.GenericAggregator import GenericAggregator
from utils.progress_bar import progress_bar
from Objects.GeneticIndividual import GeneticIndividual
from constants.constants import *


class NSGAIIAggregator(GenericAggregator):
    def __init__(self, population_size=100, mutation_rate=0.1, deviations_divider=3, **kwargs):
        super().__init__(**kwargs)

        self.population_size = population_size

        # Meta variables
        self.parent_percentage = 0.8
        self.eta = 50
        self.tournament_size = 2
        self.crossover_method = self.SBX_crossover
        self.compared_cost = "combined_cost"
        self.correction = True
        
        self.log_data = []
        self.single_log_data = []

    def set_init_variables(self, matrix, network):
        self.matrix = matrix.asformat(MATRIX_FORMAT)
        self.network = network
        self._get_actors()
        self._get_goal_balance()

        self.correction_matrix = np.ones(self.matrix.shape)
        np.fill_diagonal(self.correction_matrix, 0.)

        self.population = np.array([GeneticIndividual(self.random_start(), self.cost)
                                    for i in range(self.population_size)])

    def corrections(self, matrix):
        matrix = matrix.multiply(
            self.correction_matrix).asformat(MATRIX_FORMAT)

        matrix[matrix < 0] = 0
        matrix[matrix > self.abs_max] = self.abs_max

        return matrix.astype(int)

    def random_start(self):
        m = sc.sparse.rand(*self.matrix.shape, random())
        m *= self.abs_max
        m = self.corrections(m)

        return m

    def fast_non_dominant_sort(self):
        P = self.population
        Sx = defaultdict(list)  # dict nondominating per p
        nx = defaultdict(int)  # dict increment dominination counter of p
        xrank = np.zeros(len(P))
        Fi = []

        for pid, pv in enumerate(P):
            for qid, qv in enumerate(P):
                # if p dominates q -> less self.cost
                if getattr(pv, self.compared_cost) <= getattr(qv, self.compared_cost):
                    Sx[pid].append(qid)
                else:
                    nx[pid] += 1

            if nx[pid] == 0:
                xrank[pid] = 1
                Fi.append(pid)

        i = 1

        while Fi:
            Q = []

            for p in xrank:
                for qid, qv in Sx.items():
                    nx[qid] -= 1

                    if nx[qid] == 0:  # q belongs to the next front
                        xrank[qid] = i + 1

                        Q.append(qid)

                i += 1
                Fi = Q

        return xrank

    def crowding_distance(self, front):
        for i in front:
            i.crowding_dist = 0.

        n_solutions = len(front)

        x, y = front[0].matrix.shape

        for i in range(x):
            for j in range(y):
                sorted_solutions = sorted(front, key=lambda x: x.matrix[i, j])
                sorted_solutions, matrices = zip(
                    *[(x, x.matrix) for x in sorted_solutions])

                min_value = matrices[0][i, j]
                max_value = matrices[-1][i, j]

                sorted_solutions[0].crowding_dist += POSITIVE_INFINITY
                sorted_solutions[-1].crowding_dist += POSITIVE_INFINITY

                for s in range(1, n_solutions-1):
                    diff = matrices[s+1][i, j] - matrices[s-1][i, j]

                    if max_value - min_value == 0:
                        sorted_solutions[s].crowding_dist += 0
                    else:
                        sorted_solutions[s].crowding_dist += diff / \
                            (max_value - min_value)

    def binary_crossover(self, parent1, parent2):
        if parent1.matrix.shape != parent2.matrix.shape:
            raise Exception("Parents should have same shape")

        total = getattr(parent1, self.compared_cost) + \
            getattr(parent2, self.compared_cost)
        P1 = getattr(parent1, self.compared_cost) / total

        selection = np.random.rand(*parent1.matrix.shape) > P1

        child = parent2.matrix.copy()
        child[selection] = parent1.matrix[selection]

        return [GeneticIndividual(child, self.cost)]

    def SBX_crossover(self, parent1, parent2):
        if parent1.matrix.shape != parent2.matrix.shape:
            raise Exception("Parents should have same shape")

        b = np.random.random(parent1.matrix.shape)
        b[b < 0.5] *= 2
        b[b >= 0.5] = np.fromiter((1/(2 * (1 - x))
                                   for x in b[b >= 0.5]), float)
        b **= (1 / (self.eta + 1))

        child1 = (0.5 * (parent1.matrix.multiply((b+1)) +
                         parent2.matrix.multiply((b-1)))).astype(int)
        child2 = (0.5 * (parent1.matrix.multiply((b-1)) +
                         parent2.matrix.multiply((b+1)))).astype(int)

        return [GeneticIndividual(child1, self.cost), GeneticIndividual(child2, self.cost)]

    def tournament_selector(self, P):
        winner = choice(P)

        for _ in range(self.tournament_size-1):
            candidate = choice(P)

            if getattr(candidate, self.compared_cost) > getattr(winner, self.compared_cost):                
                winner = candidate

        return winner

    def create_children(self, parents_pop, n_children):
        while n_children != 0:
            parents = (self.tournament_selector(parents_pop),
                       self.tournament_selector(parents_pop))
            children = self.crossover_method(*parents)

            for child in children:
                n_children -= 1
                yield child

    def step(self):
        n = int(self.population_size * self.parent_percentage)

        F = self.fast_non_dominant_sort()
        fronts = sorted(list(set(F)))
        parents = []

        i = 0
        f = 1

        while len(parents) + len(F[F == f]) < n:
            self.crowding_distance(self.population[F == f])
            parents.extend(self.population[F == f])
            i += 1
            f = fronts[i]

        s = sorted(self.population[F == f],
                   key=lambda x: x.crowding_dist, reverse=True)

        parents.extend(s[:int(n - len(parents))])

        children = list(self.create_children(
            parents, int(self.population_size - n)))

        for child in children:
            child.matrix = self.mutate(child.matrix)

            if self.correction:
                child.matrix = self.corrections(child.matrix)

            child.update()

        self.population = np.array(parents + children) 

    def iterate(self, generations):
        pb = progress_bar(0, generations-1)

        for i in range(generations):
            pb(i)
            self.step()

            self.log_data.append(np.array([(x.cost, x.cons_violation, x.combined_cost)
                                           for x in self.population]).mean(axis=0))

            x = self.population[0]
            self.single_log_data.append(
                np.array([x.cost, x.cons_violation, x.combined_cost]))

    def plot_log_data(self):
        plt.figure(1, figsize=(20, 5))

        plt.subplot(131).title.set_text("cost")
        plt.plot(np.array(self.single_log_data)[:, 0])
        plt.plot(np.array(self.log_data)[:, 0])

        plt.subplot(132).title.set_text("cons_violation")
        plt.plot(np.array(self.single_log_data)[:, 1])
        plt.plot(np.array(self.log_data)[:, 1])

        plt.subplot(133).title.set_text("combined_cost")
        plt.plot(np.array(self.single_log_data)[:, 2])
        plt.plot(np.array(self.log_data)[:, 2])

        plt.show()
