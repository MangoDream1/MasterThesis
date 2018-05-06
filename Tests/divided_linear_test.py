from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.DividedLinearAggregator import DividedLinearAggregator

wrapper = simulate_aggregator(DividedLinearAggregator, 1000, None, 100)
agg = wrapper.aggregators[0]

agg.iterate(agg.get_triangles())
print(agg.plot_log_data())