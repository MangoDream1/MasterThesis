from Aggregator.SimulatedAggregator import SimulatedAggregator
from pprint import pprint

agg = SimulatedAggregator(1000, 60*60*24*7, 100)

pprint([(k, len(v)) for k, v in agg.tx_block.items()])

agg.split_into_blocks(60*60*24*3)

pprint([(k, len(v), sum(agg.block_cost(k))) for k, v in agg.tx_block.items()])