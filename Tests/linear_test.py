from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.LinearAggregator import LinearAggregator

wrapper = simulate_aggregator(LinearAggregator, 20, None, 5)
agg = wrapper.aggregators[0]

print(agg.iterate())

print(agg.start_matrix.toarray())
print(agg.matrix)