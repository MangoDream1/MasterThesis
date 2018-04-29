from AggregatorWrapper.simulate_aggregator_wrapper import simulate_aggregator
from Aggregator.GenericAggregator import GenericAggregator

from pprint import pprint

wrapper = simulate_aggregator(GenericAggregator, 1000, 60*60*24*7, 100)

pprint([(k, len(v.network.edges)) for k, v in wrapper.aggregators.items()])

wrapper.split_into_blocks(60*60*24*3)

pprint([(k, len(v.network.edges), sum(v.cost(v.matrix))) for k, v in wrapper.aggregators.items()])
