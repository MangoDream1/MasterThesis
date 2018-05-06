from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.DividedLinearAggregator import DividedLinearAggregator

wrapper = simulate_aggregator(DividedLinearAggregator, 1000, None, 100)
agg = wrapper.aggregators[0]

# agg.iterate(agg.get_connected(3))
agg.iterate(agg.get_triangles())
# agg.iterate(agg.all_combinations(3))

agg.plot_log_data()