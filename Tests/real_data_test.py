from data.reader import create_transactions, select_on_timestamp, select_on_block_height
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator

BLOCK_HEIGHTS = [496114, 496150]
TIMESTAMPS    = [1511704262, 1511781118]


selection = select_on_block_height(*BLOCK_HEIGHTS, 2)
# selection = select_on_timestamp(*TIMESTAMPS, None)

wrapper = AggregatorWrapper(DividedLinearAggregator, [selection], non_improvement=5)
agg = next(wrapper.aggregators)

print(agg.cost(agg.matrix))

agg.iterate(agg.get_loop, 3)

print(agg.cost(agg.matrix))

agg.plot_log_data()
