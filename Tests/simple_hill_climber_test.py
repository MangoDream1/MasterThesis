from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.SimpleHillClimberAggregator import SimpleHillClimber

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

wrapper = SimulatedAggregatorWrapper(SimpleHillClimber, 25, None, 5, 
            mutation_rate=0.05, deviations_divider=1000,
            non_improvement=10000)

agg = wrapper.aggregators[0]

agg.random_start()
agg.iterate()

agg.plot_log_data()

print(agg.matrix.toarray())