from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.GenericAggregator import GenericAggregator

import matplotlib.pyplot as plt
import networkx as nx

wrapper = SimulatedAggregatorWrapper(GenericAggregator, 1000, 100)
network = next(wrapper.aggregators).network

nx.draw(network, with_labels=True)
plt.show()