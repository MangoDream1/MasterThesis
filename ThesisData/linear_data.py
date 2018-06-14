from multiprocessing import Process, Queue
import time
import psutil
from threading import Event, Thread

from Objects.SimulatedTransaction import SimulatedTransaction
from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Aggregator.MultiAggregator import MultiAggregator
from Aggregator.LinearAggregator import LinearAggregator

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
        args=(10, finished_event, cut_event, q, p,))
    complete_thread = Thread(target=complete, args=(finished_event, p,))

    p.start()
    cut_off_thread.start()
    complete_thread.start()

    finished_event.wait()

    was_cut = cut_event.is_set()
    result = q.get()
    
    return result, was_cut, resource_data.cpu_percent(), resource_data.cpu_times()

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

if __name__ == '__main__':
    lin_result, mul_result = main(10, 10)

    print(lin_result)
    print(mul_result)


    