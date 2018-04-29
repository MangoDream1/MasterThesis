from Objects.SimulatedTransaction import SimulatedTransaction
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper

def simulate_aggregator(aggregator, n_transactions, time_block, amount_actors, 
    mean=1000, standard_deviation=500, timestamp_max=60*60*24*30, *args, **kwargs):

    actors = [hex(x) for x in range(amount_actors)]
    transactions = [SimulatedTransaction(actors, mean, standard_deviation, timestamp_max) 
                    for _ in range(n_transactions)]

    return AggregatorWrapper(aggregator, transactions, time_block, *args, **kwargs)