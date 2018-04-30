from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.NSGAIIAggregator import NSGAIIAggregator

import matplotlib.pyplot as plt
import networkx as nx

wrapper = simulate_aggregator(NSGAIIAggregator, 50, None, 10)
agg = wrapper.aggregators[0]

nx.draw(agg.network, with_labels=True)
plt.show()

agg.iterate(10)

agg.plot_log_data()
