from ThesisData.bitcoin_data import selection_random
from data.reader import create_transactions
import matplotlib.pyplot as plt
from utils.progress_bar import progress_bar
from ThesisData.data_constants import SAVE_NAME

import json

def count(blocks):
    size = 0
    actors = []
    for tx in create_transactions(blocks, exclude_miner_receive=True):
        actors.extend([tx.to, tx.fr])
        size += 1

    return size, len(set(actors))


if __name__ == "__main__":
    data = []
    sizes = [24, 10, 3, 1]

    # meta = 24 * 30
    # n = [int(meta/size) for size in sizes]
    n = [100 for size in sizes]

    pb = progress_bar(0, sum(n))
    p = 0

    for i, size in enumerate(sizes):
        result = []
        for blocks in selection_random(size, n[i]):
            pb(p)
            
            ntxs, nactors = count(blocks)
            if nactors:
                result.append(nactors / ntxs)

            p += 1

        data.append(result)

    with open(SAVE_NAME % ("ratio_data", "json"), "w") as f:
        json.dump(data, f)

    plt.hist(data, 25, label=["%s hours" % size for size in sizes])
    plt.legend()
    plt.show()

    for x in data:
        print(sum(x)/len(x))
