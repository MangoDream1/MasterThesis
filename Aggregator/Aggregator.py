from collections import defaultdict
import networkx as nx
import numpy as np


class Aggregator:
    def __init__(self, transactions, time_block):
        self.transactions = transactions

        self.tx_block = {}
        self.end_balance = {}
        self.networks = {}
        self.block_actors = {}

        self.split_into_blocks(time_block)

    def split_into_blocks(self, time_block):
        """
        Splits self.transactions into time blocks. If time_blocks not specified (either 0 or None), then all
        transactions put into the same block.
        :param time_block: size of each time block
        :return:
        """

        self.transactions.extend(sum(self.tx_block.values(), []))
        self.transactions = sorted(self.transactions, key=lambda tx: tx.timestamp)
        self.tx_block = defaultdict(list)

        if time_block == 0 or not time_block:
            self.tx_block[0] = self.transactions
            self.transactions = []
        else:
            min_time, max_time = self.transactions[0].timestamp, self.transactions[-1].timestamp
            time = max_time - min_time
            amount = int(time / time_block)

            for i, x in enumerate(range(amount)):
                limit = min_time + (i+1) * time_block

                while True:
                    if self.transactions[0].timestamp < limit:
                        self.tx_block[i].append(self.transactions.pop(0))
                        continue

                    break

        self._all_block_actors()
        self._blocks_end_balance()
        self._create_networks()

    def all_block_cost(self, **kwargs):
        """
        Calculate all block costs
        :param kwargs: self.block_cost keyword params
        :return: 
        """
        for k in self.tx_block.keys():
            self.block_cost(k, **kwargs)

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

        n_transactions = len(self.tx_block[block_number])

        return diff * balance_diff_multiplier + n_transactions * transaction_cost

    def _all_block_actors(self):
        """
        Creates an nested dictionary of the actor location in the end balance array
        :return: 
        """

        self.block_actors = defaultdict(lambda: defaultdict(int))

        for k, v in self.tx_block.items():
            actors = []
            for tx in v:
                actors.extend([tx.to, tx.fr])

            for i, a in enumerate(set(actors)):
                self.block_actors[k][a] = i

    def _blocks_end_balance(self):
        """
        Calculates the end balance for each actor in each block
        :return:
        """

        self.end_balance = {}
        for k in self.tx_block.keys():
            self.end_balance[k] = self._calculate_end_balance(k)

    def _calculate_end_balance(self, block_number):
        """
        Returns an np.array with the end balance, using self.block_actors for array order
        :param block_number: block number to be calculated
        :return: 
        """

        actors = self.block_actors[block_number]
        array = np.zeros(len(actors), dtype=int)
        block = self.tx_block[block_number]

        for tx in block:
            array[actors[tx.to]] += tx.amount
            array[actors[tx.fr]] -= tx.amount

        return array

    def _create_networks(self):
        """
        Creates networks for each block and saves in self.network with same key as self.tx_block
        :return:
        """

        for k, v in self.tx_block.items():
            directed_graph = nx.DiGraph()
            edges = [tx.get_graph_edge() for tx in v]
            directed_graph.add_weighted_edges_from(edges)

            self.networks[k] = directed_graph
