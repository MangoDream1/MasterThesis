from Aggregator.SimulatedAggregator import SimulatedAggregator
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


agg = SimulatedAggregator(10, None, 5)

nx.draw(agg.networks[0], with_labels=True)
plt.show()

agg.simple_hill_climber(0)

nx.draw(agg.networks[0], with_labels=True)
plt.show()

print(agg.matrices[0].toarray())

