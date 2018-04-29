from Aggregator.GenericAggregator import GenericAggregator
from Objects.SimulatedTransaction import SimulatedTransaction


def simulate_aggregator(aggregator, n_transactions, time_block, amount_actors, 
    transaction_cost=100, balance_diff_multiplier=10, **kwargs):

    actors = [hex(x) for x in range(amount_actors)]
    transactions = [SimulatedTransaction(actors, **kwargs) for _ in range(n_transactions)]

    return aggregator(transactions, time_block, transaction_cost=transaction_cost, 
                        balance_diff_multiplier=balance_diff_multiplier)