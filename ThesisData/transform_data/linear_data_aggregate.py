import json
import pprint
from collections import defaultdict
from itertools import chain
import numpy as np

from ThesisData.data_constants import SAVE_NAME

load_file = SAVE_NAME % ("linear_data", "json")
save_file = SAVE_NAME % ("linear_data_agg", "json")

with open(load_file, "r") as f:
    data = json.load(f)

def flatten_dicts(dicts):
    dicts = map(lambda x: x.items(), dicts)
    result = defaultdict(list)
    
    for k, v in chain(*dicts):
        result[k].append(v)
        
    return result

def average_flat_dicts(dicts):
    flat = flatten_dicts(dicts)
    result = {}
        
    for k, v in flat.items():
        mean = np.array(v).mean(axis=0)

        if (type(mean) == np.ndarray):
            mean = list(mean)

        result[k] = mean
        
    return result

def average_dicts(dicts):
    length = len(dicts)
    dicts = map(lambda x: x.items(), dicts)
    result = defaultdict(int)
    
    for k, v in chain(*dicts):
        result[k] += v
        
    for k in result.keys():
        result[k] /= length
        
    return result

lists = []
order = []
for n_actors in data.keys():
    for n_txs in data[n_actors].keys():
        order.append((n_actors, n_txs))
        lists.append(data[n_actors][n_txs].values())

first = next(iter(lists[0]))
types = list(first.keys())
value_names = list(first[types[0]].keys())

aggregated_list = []
for lst in lists:
    aggregated = defaultdict(lambda: defaultdict(list))

    for dct in lst:
        for t in types:
            for name in value_names:
                aggregated[t][name].append(dct[t][name])
                
    aggregated_list.append(aggregated)
        
for aggregated in aggregated_list:
    cuts = []
    
    for t in types:
        cuts.append(aggregated[t]["was_cut"])
        
    cuts = np.array(cuts).sum(axis=0)==0
    
    for t in types:
        current = aggregated[t]
        current["result"] = average_dicts(
            np.array(current["result"])[cuts])
        current["resources"] = average_flat_dicts(
            np.array(current["resources"])[cuts])
        current["was_cut"] = sum(current["was_cut"]) / len(current["was_cut"])
        
        s_txs = current["result"]["start_n_txs"]
        cost  = current["result"]["result_cost"]

        current["result"]["reduction"] = (s_txs - cost) / s_txs 

i = 0

result = defaultdict(dict)
for n_actors, n_txs in order:
    result[n_actors][n_txs] = aggregated_list[i]
    i += 1

with open(save_file, "w") as f:
    json.dump(result, f, indent=4, sort_keys=True)