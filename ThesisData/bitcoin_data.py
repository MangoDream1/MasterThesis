from datetime import datetime, timedelta
import json
import sys
from random import randint
from pprint import pprint
from multiprocessing import Pool


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

def selection_sequential(hours,n):
    BEGIN_DATE = datetime(2017, 1, 1)
    TIMESTAMPS = []    

    start = BEGIN_DATE

    for _ in range(n):
        end = start + timedelta(hours=hours)
        TIMESTAMPS.append((start.timestamp(), end.timestamp()))
        start = end

    selection = [select_on_timestamp(*ts, None) for ts in TIMESTAMPS]
    
    print("Start block:\t", selection[0][0])
    print("End block:\t", selection[-1][-1])

    return selection 

def selection_random(hours,n):
    TIMESTAMPS = []    

    for _ in range(n):
        while True:
            try:
                start = datetime(2017, randint(1, 12), randint(1, 31))
                break
            except ValueError:
                pass

        end = start + timedelta(hours=hours)
        TIMESTAMPS.append((start.timestamp(), end.timestamp()))

    selection = [select_on_timestamp(*ts, None) for ts in TIMESTAMPS]

    return selection

def selection_random_blocks(n):
    selection = selection_random(1, n)

    return [[x[0]] for x in selection]

def solve_hours(hours, n, name):
    # selection = selection_sequential(hours,n)
    # selection = selection_random(hours, n)
    selection = selection_random_blocks(n)
    pprint(selection)    

    print("Total number of blocks: ", sum(len(x) for x in selection))
    print("Blocks per bin: ", [len(x) for x in selection])

    pool = Pool()
    
    wrapper = AggregatorWrapper(MultiAggregator, DividedLinearAggregator, func=method, pool=pool)
    wrapper.create_aggregators_from_selections(selection)

    for agg in wrapper.aggregators:
        print(agg.cost(agg.matrix), agg.matrix.shape)

        agg.iterate()

        print(agg.cost(agg.matrix), agg.matrix.shape)
        
        with open(SAVE_NAME % (name, "json"), "w") as f:
            # needed for a strange problem with defaultdict and json
            dct = dict(wrapper.result)
            dct = {x: {k: int(v) for k, v in inner.items() if v != None} for x, inner in dct.items()}

            json.dump(dct, f)
        
if __name__ == "__main__":
    hour_bin = 1
    n = 24
    name = "bitcoin_%shour_data" % hour_bin

    if len(sys.argv) > 3:
        hour_bin = int(sys.argv[1])
        n = int(sys.argv[2])
        name = sys.argv[3]

    solve_hours(hour_bin, n, name)
