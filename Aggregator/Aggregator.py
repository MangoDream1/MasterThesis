from collections import defaultdict
import networkx as nx
import numpy as np
from random import *


class Aggregator:
    def __init__(self, transactions, time_block, transaction_cost=100, balance_diff_multiplier=10):
        self.transactions = transactions

        self.goal_balance = {}
        self.networks = {}
        self.block_actors = {}

        self.split_into_blocks(time_block)

        self.transaction_cost = transaction_cost
        self.balance_diff_multiplier = balance_diff_multiplier

    def simple_hill_climber(self, block_number):
        print("Pre-cost", sum(self.block_cost(block_number)))

        network = self.networks[block_number]
        network.remove_edges_from(list(network.edges()))

        diff_cost, tx_cost = self.block_cost(block_number)
        cost = diff_cost + tx_cost

        non_improvement = 0
        i = 0

        print("Init cost %s" % cost, diff_cost, tx_cost )

        while non_improvement <= 1000 and cost != 0:
            old_network = self.networks[block_number].copy()

            self._add_random_transaction(block_number, diff_cost)
            n_diff_cost, n_tx_cost = self.block_cost(block_number)
            n_cost = n_diff_cost + n_tx_cost

            if n_cost > cost:
                non_improvement += 1
                self.networks[block_number] = old_network
            else:
                i += 1
                non_improvement = 0
                diff_cost = n_diff_cost
                cost = n_cost

            # print("Iteration: %s Cost: %s Edges: %s" % (i, cost, self.networks[block_number].number_of_edges()))

        print("Last cost %s" % cost, diff_cost, tx_cost)


    def split_into_blocks(self, time_block):
        """
        Splits self.transactions into time blocks. If time_blocks not specified (either 0 or None), then all
        transactions put into the same block.
        :param time_block: size of each time block
        :return:
        """

        self.transactions = sorted(self.transactions, key=lambda tx: tx.timestamp)
        tx_block = defaultdict(list)

        if time_block == 0 or not time_block:
            tx_block[0] = self.transactions
            self.transactions = []
        else:
            min_time, max_time = self.transactions[0].timestamp, self.transactions[-1].timestamp
            time = max_time - min_time
            amount = int(time / time_block)

            transactions = []

            for i, x in enumerate(range(amount)):
                limit = min_time + (i+1) * time_block

                while True:
                    if self.transactions[0].timestamp < limit:
                        popped = self.transactions.pop(0)
                        tx_block[i].append(popped)
                        transactions.append(popped)
                        continue

                    break

            self.transactions = transactions

        self._create_networks(tx_block)
        self._all_block_actors()
        self._blocks_end_balance()

    def all_block_cost(self):
        """
        Calculate all block costs
        :return: 
        """

        return [self.block_cost(k) for k in self.networks.keys()]

    def block_cost(self, block_number):
        """
        Calculates the cost of a block
        :param block_number: The block
        :return: 
        """

        end_balance = self._calculate_end_balance(block_number)
        diff = sum(np.absolute(end_balance - self.goal_balance[block_number]))

        n_transactions = self.networks[block_number].number_of_edges()

        return diff * self.balance_diff_multiplier, n_transactions * self.transaction_cost

    def _all_block_actors(self):
        """
        Creates an nested dictionary of the actor location in the end balance array
        :return: 
        """

        self.block_actors = defaultdict(lambda: defaultdict(int))

        for k, network in self.networks.items():
            actors = []
            for to, fr in network.edges():
                actors.extend([to, fr])

            for i, a in enumerate(set(actors)):
                self.block_actors[k][a] = i

    def _blocks_end_balance(self):
        """
        Calculates the end balance for each actor in each block
        :return:
        """

        self.goal_balance = {}
        for k in self.networks.keys():
            self.goal_balance[k] = self._calculate_end_balance(k)

    def _calculate_end_balance(self, block_number):
        """
        Returns an np.array with the end balance, using self.block_actors for array order
        :param block_number: block number to be calculated
        :return: 
        """

        actors = self.block_actors[block_number]
        array = np.zeros(len(actors), dtype=int)
        network = self.networks[block_number]

        for to, fr, amount in network.edges.data('weight'):
            array[actors[to]] += amount
            array[actors[fr]] -= amount

        return array

    def _create_networks(self, tx_block):
        """
        Creates networks for each block and saves in self.network with same key as tx_block
        :param tx_block: nested list with all transactions per block
        :return:
        """

        for k, v in tx_block.items():
            directed_graph = nx.DiGraph()
            edges = [tx.get_graph_edge() for tx in v]

            # joins edges from and to same location
            joined = defaultdict(int)
            for to, fr, amount in edges:
                joined[(to, fr)] += amount

            edges = [(to, fr, amount) for (to, fr), amount in joined.items()]
            directed_graph.add_weighted_edges_from(edges)

            self.networks[k] = directed_graph

    def _add_random_transaction(self, block_number, balance_diff_cost):
        actors = list(self.block_actors[block_number].keys())
        network = self.networks[block_number]

        to = choice(actors)
        fr = choice(actors)

        while fr == to:
            to = choice(actors)

        amount = int(normalvariate(0, 100))

        # If edge already exists add to the edge, if weight less than 0 remove edge
        if network.number_of_edges(to, fr) > 0:
            weight = network[to][fr]["weight"] + amount

            if weight <= 0:
                network.remove_edge(to, fr)
                return

            network[to][fr]["weight"] = weight
            return

        network.add_edge(to, fr, weight=amount)
