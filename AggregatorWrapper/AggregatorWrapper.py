from collections import defaultdict
import networkx as nx

from data.reader import create_transactions

class AggregatorWrapper:
    def __init__(self, Aggregator, selections, *args, **kwargs):
        self._Aggregator = Aggregator
        self._args = args
        self._kwargs = kwargs

        self.aggregators = self.create_aggregators(selections)

    def create_aggregators(self, selections):
        for selection in selections:
            txs = list(create_transactions(selection))

            agg = self._Aggregator(*self._args, **self._kwargs)

            network = self._create_network(txs)
            matrix = nx.to_scipy_sparse_matrix(network)

            agg.set_init_variables(matrix, network)

            yield agg

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
