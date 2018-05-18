from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.LinearAggregator import LinearAggregator

wrapper = SimulatedAggregatorWrapper(LinearAggregator, 20, 5)
agg = next(wrapper.aggregators)

print(agg.iterate())

print(agg.start_matrix.toarray())
print(agg.matrix)