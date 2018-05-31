from data.berka_reader import get_transactions
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper

txs = get_transactions()

wrapper = AggregatorWrapper(DividedLinearAggregator)
wrapper.create_aggregators_from_tx_lists(txs)

agg = next(wrapper.aggregators)
print(agg.cost(agg.matrix))

agg.iterate(agg.get_crosses)
print(agg.cost(agg.matrix))

agg.iterate(agg.get_loop, 3)
print(agg.cost(agg.matrix))

agg.plot_log_data()