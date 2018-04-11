from Aggregator.SimulatedAggregator import SimulatedAggregator
from pprint import pprint

agg = SimulatedAggregator(1000, 60*60*24*7, 100)

pprint(agg.tx_block)
pprint(agg.end_balance)