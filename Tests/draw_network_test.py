from Aggregator.SimulatedAggregator import SimulatedAggregator
import matplotlib.pyplot as plt
import networkx as nx

agg = SimulatedAggregator(1000, 60*60*24*7, 100)
network = agg.networks[0]

nx.draw(network, with_labels=True)
plt.show()