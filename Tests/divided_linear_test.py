from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.DividedLinearAggregator import DividedLinearAggregator

wrapper = simulate_aggregator(DividedLinearAggregator, 1000, None, 100)
agg = wrapper.aggregators[0]

print(agg.cost(agg.matrix))

agg.iterate(agg.get_loop, 3)
# agg.iterate(agg.get_triangles)

print(agg.cost(agg.matrix))

agg.iterate(agg.get_loop, 4)

# print(agg.cost(agg.matrix))

# agg.iterate(agg.get_loop, 5)

print(agg.cost(agg.matrix))

agg.plot_log_data()