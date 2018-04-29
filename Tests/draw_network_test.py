from Aggregator.simulate_aggregator import simulate_aggregator
from Aggregator.GenericAggregator import GenericAggregator

import matplotlib.pyplot as plt
import networkx as nx

agg = simulate_aggregator(GenericAggregator, 1000, 60*60*24*7, 100)
network = agg.networks[0]

nx.draw(network, with_labels=True)
plt.show()