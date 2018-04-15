from collections import defaultdict
import networkx as nx
import numpy as np
from random import choice


class Aggregator:
    def __init__(self, transactions, time_block):
        self.transactions = transactions

        self.end_balance = {}

        self.networks = {}
        self.block_actors = {}
        self.block_limit = {}

        self.split_into_blocks(time_block)

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
                self.block_limit[i] = limit

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

    def all_block_cost(self, **kwargs):
        """
        Calculate all block costs
        :param kwargs: self.block_cost keyword params
        :return: 
        """

        return [self.block_cost(k, **kwargs) for k in self.networks.keys()]

    def block_cost(self, block_number, transaction_cost=100, balance_diff_multiplier=4):
        """
        Calculates the cost of a block
        :param block_number: The block
        :param transaction_cost: the cost per transaction
        :param balance_diff_multiplier: the multiplier of difference between wanted end balance and block end balance
        :return: 
        """

        end_balance = self._calculate_end_balance(block_number)
        diff = sum(np.absolute(end_balance - self.end_balance[block_number]))

        n_transactions = self.networks[block_number].number_of_edges()

        return diff * balance_diff_multiplier, n_transactions * transaction_cost

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

        self.end_balance = {}
        for k in self.networks.keys():
            self.end_balance[k] = self._calculate_end_balance(k)

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
        actors = self.block_actors[block_number].keys()
        network = self.networks[block_number]

        to = choice(actors)
        fr = choice(actors)

        while fr == to:
            to = choice(actors)

        # FIXME find a better amount relative to the cost
        amount = 1

        # If edge already exists add to the edge
        if network.number_of_edges(to, fr) > 0:
            network[to][fr]["weight"] += amount
        else:
            network.add_edge(to, fr, weight=amount)
