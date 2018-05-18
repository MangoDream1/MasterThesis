from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator

wrapper = SimulatedAggregatorWrapper(DividedLinearAggregator, 1000, None, 100)
agg = wrapper.aggregators[0]

print(agg.cost(agg.matrix))

agg.iterate(agg.get_loop, 3)

print(agg.cost(agg.matrix))

agg.iterate(agg.get_loop, 4)

# print(agg.cost(agg.matrix))

# agg.iterate(agg.get_loop, 5)

print(agg.cost(agg.matrix))

agg.plot_log_data()