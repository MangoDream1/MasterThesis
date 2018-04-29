from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.NSGAIIAggregator import NSGAIIAggregator

import matplotlib.pyplot as plt
import networkx as nx

wrapper = simulate_aggregator(NSGAIIAggregator, 50, None, 10)
network = wrapper.aggregators[0].network

nx.draw(network, with_labels=True)
plt.show()

# TODO make it do genetic algorithm