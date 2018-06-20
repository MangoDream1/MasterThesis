from multiprocessing import Process, Queue
import time
import psutil
from threading import Event, Thread
import json
import os

from Objects.SimulatedTransaction import SimulatedTransaction
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Aggregator.MultiAggregator import MultiAggregator
from Aggregator.LinearAggregator import LinearAggregator
from ThesisData.data_constants import SAVE_NAME
from utils.progress_bar import progress_bar

def cut_off(n, finished_event, cut_event, queue, process):    
    while n != 0:
        time.sleep(1)

        if finished_event.is_set():
            break
        
        n -= 1

    if not finished_event.is_set():
        process.terminate()
        finished_event.set()
        cut_event.set()
        queue.put(None)

def complete(finished_event, process):
    process.join()

    if not finished_event.is_set():
        finished_event.set()

def start(func, args, kwargs={}):
    q = Queue()

    kwargs["queue"] = q
    p = Process(target=func, args=args, kwargs=kwargs)

    resource_data = psutil.Process(p.pid)
    resource_data.cpu_percent()

    finished_event = Event()
    cut_event      = Event()

    cut_off_thread  = Thread(target=cut_off, 
        args=(60*5, finished_event, cut_event, q, p,))
    complete_thread = Thread(target=complete, args=(finished_event, p,))

    p.start()
    cut_off_thread.start()
    complete_thread.start()

    finished_event.wait()

    was_cut = cut_event.is_set()
    result = q.get()
    
    return {
        "result": result,
        "was_cut": was_cut,
        "resources": resource_data.as_dict(attrs=["cpu_percent", "cpu_times"])
    }
        
def aggregate(Aggregator, transactions, args, kwargs, queue):
    wrapper = AggregatorWrapper(Aggregator, *args, **kwargs)
    wrapper.create_aggregators_from_tx_lists([transactions])
    agg = next(wrapper.aggregators)

    agg.iterate()

    queue.put(agg.result)

def selection_method(agg):
    agg.iterate(agg.get_crosses)
    for x in [3, 4, 5, 6]:
        agg.iterate(agg.get_loop, x)

def main(n_actors, n_transactions):
    actors = [hex(x) for x in range(n_actors)]
    transactions = [SimulatedTransaction(actors, 1000, 500, 60*60*24*30) 
                    for _ in range(n_transactions)]

    lin_result = start(aggregate, (LinearAggregator, transactions, (), {}))
    mul_result = start(aggregate, (MultiAggregator, transactions, 
        (DividedLinearAggregator, ), {"func": selection_method, "progress": False}))

    return lin_result, mul_result

def fix_dct(dct):
    if not dct:
        return None

    # needed for a strange problem with defaultdict and json
    return {k: int(v) for k, v in dct.items() if v != None}

if __name__ == '__main__':
    ACTORS_SIZES = ["10", "25", "50"]
    TX_SIZES     = ["10", "50", "100", "500"]
    n_iterations = 50

    save_file = SAVE_NAME % ("linear_data", "json")

    data = {}

    if os.path.isfile(save_file):
        with open(save_file, "r") as f:
            data = json.load(f)

    pb = progress_bar(0, len(ACTORS_SIZES) * len(TX_SIZES) * n_iterations)
    progress = 0

    for n_actors in ACTORS_SIZES:
        if n_actors not in data:
            data[n_actors] = {}            

        for n_txs in TX_SIZES:
            if n_txs not in data[n_actors]:
                data[n_actors][n_txs] = {}

            done = data[n_actors][n_txs].keys()

            for i in range(n_iterations):
                pb(progress)
                progress += 1

                if str(i) in done:
                    continue
                
                lin_result, mul_result = main(int(n_actors), int(n_txs))

                lin_result["result"] = fix_dct(lin_result["result"])
                mul_result["result"] = fix_dct(mul_result["result"])

                data[n_actors][n_txs][str(i)] = {}
                data[n_actors][n_txs][str(i)]["gurobi"] = lin_result
                data[n_actors][n_txs][str(i)]["heuristics"] = mul_result

                with open(save_file, "w") as f:
                    json.dump(data, f, indent=4, sort_keys=True)



    