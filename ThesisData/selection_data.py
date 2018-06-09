from collections import defaultdict
import pprint
import json
from decimal import Decimal

from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Objects.SimulatedTransaction import SimulatedTransaction
from ThesisData.data_constants import SAVE_NAME
from utils.progress_bar import progress_bar

amount_actors = 100
actors = [hex(x) for x in range(amount_actors)]

def combi1(agg):
    agg.iterate(agg.get_loop, 3)
    agg.iterate(agg.get_loop, 4)
    agg.iterate(agg.get_loop, 5)
    agg.iterate(agg.get_crosses, 5, 50)

def combi2(agg):
    agg.iterate(agg.get_crosses, 5, 50)
    agg.iterate(agg.get_loop, 3)
    agg.iterate(agg.get_loop, 4)
    agg.iterate(agg.get_loop, 5)

methods = [
    ("clique50", lambda agg: agg.iterate(agg.get_cliques, 50)),
    ("loop3", lambda agg: agg.iterate(agg.get_loop, 3)),
    ("loop4", lambda agg: agg.iterate(agg.get_loop, 4)),
    ("loop5", lambda agg: agg.iterate(agg.get_loop, 5)),
    ("cross5", lambda agg: agg.iterate(agg.get_crosses, 5, 50)),
    ("cross10", lambda agg: agg.iterate(agg.get_crosses, 10, 50)),    
    ("loops+cross", combi1), 
    ("cross+loop", combi2)   
]

data = defaultdict(lambda: defaultdict(list))
n_iterations = 10
transaction_sizes = [100, 500, 1000]

pb = progress_bar(0, n_iterations * len(transaction_sizes) * len(methods))
i = 0

for n_transactions in transaction_sizes:
    for _ in range(n_iterations):
    
        transactions = [SimulatedTransaction(actors, 1000, 500, 60*60*24*30) 
                        for _ in range(n_transactions)]

        for name, method in methods:
            pb(i)

            wrapper = AggregatorWrapper(DividedLinearAggregator)
            wrapper.create_aggregators_from_tx_lists([transactions])
            agg = next(wrapper.aggregators)

            method(agg)

            total = sum(agg.component_data.values())
            agg.component_data["total"] = total

            data[name][n_transactions].append({**agg.result, **agg.component_data})
            i += 1

    for name, _ in methods:
        average = defaultdict(int)

        for dct in data[name][n_transactions]:
            for k, v in dct.items():
                if v:
                    average[k] += v / n_iterations
        
        d = Decimal((n_transactions - average["total"]) / average["result_cost"])

        average["ratio"] = format(d, ".2e")
        data[name][n_transactions] = average
        
    with open(SAVE_NAME % "selection_data", "w") as f:
                json.dump(data, f, indent=3)

    print("finsished ", n_transactions)

