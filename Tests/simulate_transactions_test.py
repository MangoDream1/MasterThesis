from Aggregator.simulate_aggregator import simulate_aggregator
from Aggregator.GenericAggregator import GenericAggregator

from pprint import pprint

agg = simulate_aggregator(GenericAggregator, 1000, 60*60*24*7, 100)

pprint([(k, len(v)) for k, v in agg.networks.items()])

agg.split_into_blocks(60*60*24*3)

pprint([(k, len(v), sum(agg.block_cost(agg.matrices[k], agg.goal_balance[k]))) for k, v in agg.networks.items()])