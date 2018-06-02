from Objects.SimulatedTransaction import SimulatedTransaction
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
import networkx as nx

class SimulatedAggregatorWrapper(AggregatorWrapper):
    def __init__(self, Aggregator, n_transactions, amount_actors, *args,
                 mean=1000, standard_deviation=500, timestamp_max=60*60*24*30, **kwargs):
        actors = [hex(x) for x in range(amount_actors)]
        transactions = [SimulatedTransaction(actors, mean, standard_deviation, timestamp_max) 
                        for _ in range(n_transactions)]

        super().__init__(Aggregator, *args, **kwargs)

        self.create_aggregators_from_tx_lists([transactions])

    def create_aggregators_from_selections(self):
        pass