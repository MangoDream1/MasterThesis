from AggregatorWrapper.simulate_aggregator_wrapper import SimulatedAggregatorWrapper
from Aggregator.NSGAIIAggregator import NSGAIIAggregator

import matplotlib.pyplot as plt
import networkx as nx

wrapper = SimulatedAggregatorWrapper(NSGAIIAggregator, 50, None, 10)
agg = wrapper.aggregators[0]

nx.draw(agg.network, with_labels=True)
plt.show()

agg.iterate(10000)

agg.plot_log_data()
