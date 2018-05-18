from Objects.SimulatedTransaction import SimulatedTransaction
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
import networkx as nx

class SimulatedAggregatorWrapper(AggregatorWrapper):
    def __init__(self, Aggregator, n_transactions, time_block, amount_actors, 
                 mean=1000, standard_deviation=500, timestamp_max=60*60*24*30, *args, **kwargs):

        actors = [hex(x) for x in range(amount_actors)]
        self.transactions = [SimulatedTransaction(actors, mean, standard_deviation, timestamp_max) 
                             for _ in range(n_transactions)]

        aggregator = Aggregator(*args, **kwargs)
        network = self._create_network(self.transactions)
        matrix = nx.to_scipy_sparse_matrix(network)

        aggregator.set_init_variables(matrix, network)

        self.aggregators = {0: aggregator}
