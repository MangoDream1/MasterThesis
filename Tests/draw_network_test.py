from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.GenericAggregator import GenericAggregator

import matplotlib.pyplot as plt
import networkx as nx

wrapper = SimulatedAggregatorWrapper(GenericAggregator, 1000, 60*60*24*7, 100)
network = wrapper.aggregators[0].network

nx.draw(network, with_labels=True)
plt.show()