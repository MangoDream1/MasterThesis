from datetime import datetime, timedelta
import json
import sys
from random import randint
from pprint import pprint
from multiprocessing import Pool
from threading import Thread

from data.reader import create_transactions, select_on_timestamp, select_on_block_height

from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Aggregator.MultiAggregator import MultiAggregator
from ThesisData.data_constants import SAVE_NAME
from Objects.SimulatedTransaction import SimulatedTransaction


def method(agg):
    agg.iterate(agg.get_crosses, 5, 20)
    for x in [3, 4, 5, 6]:
        agg.iterate(agg.get_loop, x)

def selection_sequential(hours,n):
    BEGIN_DATE = datetime(2017, 1, 1)

    start = BEGIN_DATE

    for _ in range(n):
        end = start + timedelta(hours=hours)
        yield select_on_timestamp(start.timestamp(), end.timestamp(), None)
        start = end

def selection_random(hours,n):
    previous = []    

    for _ in range(n):
        while True:
            try:
                start = datetime(2017, randint(1, 12), randint(1, 31))                
            except ValueError:
                pass

            allowed = True
            for s, e in previous:
                if start >= s and start <= e:
                    allowed = False
                    break

            if not allowed:
                continue

            end = start + timedelta(hours=hours)
            previous.append((start, end)) # all hours inside this window not possible for others 

            break

        yield select_on_timestamp(start.timestamp(), end.timestamp(), None)

def selection_random_blocks(n):
    for x in selection_random(1, n):
        yield x[0]

def save_result(name, wrapper):
    with open(SAVE_NAME % (name, "json"), "w") as f:
        # needed for a strange problem with defaultdict and json
        dct = dict(wrapper.result)
        dct = {x: {k: int(v) for k, v in inner.items() if v != None} for x, inner in dct.items()}

        json.dump(dct, f, indent=4)

def solve_hours(hours, n, name):
    # selection = list(selection_sequential(hours,n))
    selection = list(selection_random(hours, n))
    # selection = list(selection_random_blocks(n))
    pprint(selection)    

    print("Total number of blocks: ", sum(len(x) for x in selection))
    print("Blocks per bin: ", [len(x) for x in selection])

    pool = Pool()
    
    wrapper = AggregatorWrapper(MultiAggregator, DividedLinearAggregator, func=method, pool=pool, stop=True)
    wrapper.create_aggregators_from_selections(selection)

    # actors = [hex(x) for x in range(1000)]
    # transactions = [SimulatedTransaction(actors, 1000, 500, 60*60*24*30) 
    #                 for _ in range(500)]

    # wrapper.create_aggregators_from_tx_lists([transactions]*10)

    def process(agg):
        print(agg.cost(agg.matrix), agg.matrix.shape)

        agg.iterate()

        print("\n", agg.cost(agg.matrix), agg.matrix.shape)
        
    threads = []
    for agg in wrapper.aggregators:
        t = Thread(target=process, args=(agg,))
        threads.append(t)

        t.start()

        agg.final_stretch_event.wait()
        save_result(name, wrapper)
        
    for t in threads:
        t.join()
        
    save_result(name, wrapper)

if __name__ == "__main__":
    hour_bin = 1
    n = 10
    name = "bitcoin_%shour_data" % hour_bin

    if len(sys.argv) > 3:
        hour_bin = int(sys.argv[1])
        n = int(sys.argv[2])
        name = sys.argv[3]

    solve_hours(hour_bin, n, name)
