from collections import defaultdict

import networkx as nx


class AggregatorWrapper:
    def __init__(self, Aggregator, transactions, time_block, *args, **kwargs):
        self.transactions = transactions

        self.aggregators = defaultdict(lambda: Aggregator(*args, **kwargs))

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
        else:
            min_time, max_time = self.transactions[0].timestamp, self.transactions[-1].timestamp
            time = max_time - min_time
            amount = int(time / time_block)

            transactions = []

            for i in range(amount):
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

    def _create_networks(self, tx_block):
        """
        Calls _create_network for all items in tx_block and sets it to appropiate aggregator
        :param tx_block: nested list with all transactions per block
        :return:
        """

        for k, v in tx_block.items():
            network = self._create_network(v)

            self.aggregators[k].set_init_variables(
                nx.to_scipy_sparse_matrix(network), network)

    @staticmethod
    def _create_network(transactions):
        """
        Creates network from a transactions list; joins transactions having the same to and fr
        :param transactions: list of Transaction objects
        :return: directed graph
        """

        edges = [tx.get_graph_edge() for tx in transactions]

        # joins edges from and to same location
        joined = defaultdict(int)
        for to, fr, amount in edges:
            joined[(to, fr)] += amount

        edges = [(to, fr, amount) for (to, fr), amount in joined.items()]
        
        directed_graph = nx.DiGraph()
        directed_graph.add_weighted_edges_from(edges)

        return directed_graph
