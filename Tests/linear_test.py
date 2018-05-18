from AggregatorWrapper.simulate_aggregator_wrapper import SimulatedAggregatorWrapper
from Aggregator.LinearAggregator import LinearAggregator

wrapper = SimulatedAggregatorWrapper(LinearAggregator, 20, None, 5)
agg = wrapper.aggregators[0]

print(agg.iterate())

print(agg.start_matrix.toarray())
print(agg.matrix)