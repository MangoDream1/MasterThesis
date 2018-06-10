from datetime import datetime, timedelta
import json
import sys

from data.reader import create_transactions, select_on_timestamp, select_on_block_height

from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Aggregator.MultiAggregator import MultiAggregator
from ThesisData.data_constants import SAVE_NAME


def method(agg):
    agg.iterate(agg.get_crosses)
    for x in [3, 4, 5, 6]:
        agg.iterate(agg.get_loop, x)

def solve_hours(hours, n):
    BEGIN_DATE = datetime(2017, 1, 1)
    TIMESTAMPS = []    

    start = BEGIN_DATE

    for _ in range(n):
        end = start + timedelta(hours=hours)
        TIMESTAMPS.append((start.timestamp(), end.timestamp()))
        start = end

    selection = [select_on_timestamp(*ts, None) for ts in TIMESTAMPS]

    print("Total number of blocks: ", sum(len(x) for x in selection))
    print("Blocks per bin: ", [len(x) for x in selection])
    print("Start block:\t", selection[0][0])
    print("End block:\t", selection[-1][-1])
    
    wrapper = AggregatorWrapper(MultiAggregator, DividedLinearAggregator, func=method)
    wrapper.create_aggregators_from_selections(selection)

    for agg in wrapper.aggregators:
        print(agg.cost(agg.matrix), agg.matrix.shape)

        agg.iterate()

        with open(SAVE_NAME % ("bitcoin_%shour_data" % hours, "json"), "w") as f:
            json.dump(wrapper.result, f)
        
if __name__ == "__main__":
    hour_bin = 1
    n = 24

    if len(sys.argv) > 2:
        hour_bin = int(sys.argv[-2])
        n = int(sys.argv[-1])

    solve_hours(hour_bin, n)
