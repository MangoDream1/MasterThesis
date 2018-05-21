from collections import defaultdict
import networkx as nx

from data.reader import create_transactions

class AggregatorWrapper:
    def __init__(self, Aggregator, selections, exclude_miner_receive=True, *args, **kwargs):
        self._Aggregator = Aggregator
        self._args = args
        self._kwargs = kwargs
        self.exclude_miner_receive = exclude_miner_receive

        self.aggregators = self.create_aggregators(selections)

        self.result = defaultdict(lambda: {
            "result_cost": None,
            "result_cons": None,
            "start_n_txs": None,
            "n_actors":    None,
            "bitcoin_txs": None
        })

    def create_aggregators(self, selections):
        for i, selection in enumerate(selections):
            txs = list(create_transactions(selection, exclude_miner_receive=self.exclude_miner_receive))

            self.result[i]["bitcoin_txs"] = sum(int(x.split("_")[2]) for x in selection)
            yield from self._create_aggregator(i, txs)

    def _create_aggregator(self, i, txs):
        agg = self._Aggregator(*self._args, result=self.result[i], **self._kwargs)

        network = self._create_network(txs)
        matrix = nx.to_scipy_sparse_matrix(network)

        agg.set_init_variables(matrix, network)

        self.result[i]["start_n_txs"] = len(txs)
        self.result[i]["n_actors"] = network.number_of_nodes()

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
