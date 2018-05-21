from Objects.SimulatedTransaction import SimulatedTransaction
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
import networkx as nx

class SimulatedAggregatorWrapper(AggregatorWrapper):
    def __init__(self, Aggregator, n_transactions, amount_actors, 
                 mean=1000, standard_deviation=500, timestamp_max=60*60*24*30, *args, **kwargs):

        actors = [hex(x) for x in range(amount_actors)]
        transactions = [SimulatedTransaction(actors, mean, standard_deviation, timestamp_max) 
                        for _ in range(n_transactions)]

        super().__init__(Aggregator, transactions)

    def create_aggregators(self, txs):
        yield from self._create_aggregator(0, txs)
