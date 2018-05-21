from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator

wrapper = SimulatedAggregatorWrapper(DividedLinearAggregator, 1000, 100)
agg = next(wrapper.aggregators)

print(agg.cost(agg.matrix))

for x in [3, 4, 5, 6]:
    agg.iterate(agg.get_loop, x)
    print(agg.cost(agg.matrix))

agg.plot_log_data()
print(wrapper.result[0])