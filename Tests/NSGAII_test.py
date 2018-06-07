from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.NSGAIIAggregator import NSGAIIAggregator

import matplotlib.pyplot as plt
import networkx as nx

wrapper = SimulatedAggregatorWrapper(NSGAIIAggregator, 50, 10)
agg = next(wrapper.aggregators)

nx.draw(agg.network, with_labels=True)
plt.show()

print(agg.cost(agg.matrix))


agg.iterate(10000)

print(agg.cost(agg.matrix))

agg.plot_log_data()
