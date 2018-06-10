def selection_method(agg):
    agg.iterate(agg.get_crosses, 5, 50)
    for x in [3, 4, 5, 6]:
        agg.iterate(agg.get_loop, x)

if __name__ == "__main__":
    from ThesisData.data_constants import SAVE_NAME
    from decimal import Decimal
    from utils.progress_bar import progress_bar

    from Aggregator.DividedLinearAggregator import DividedLinearAggregator
    from Aggregator.MultiAggregator import MultiAggregator
    from Objects.SimulatedTransaction import SimulatedTransaction
    from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
    from multiprocessing import Pool
    

    ACTORS_SIZES = [50, 100, 500, 1000, 5000]
    TX_SIZES     = [50, 100, 500, 1000, 5000]
    n_iterations = 10

    pool_size = 8
    pool = Pool(pool_size)

    pb = progress_bar(0, len(ACTORS_SIZES) * len(TX_SIZES) * n_iterations)
    i = 0

    for n_actors in ACTORS_SIZES:
        actors = [hex(x) for x in range(n_actors)]

        for n_txs in TX_SIZES:
            costs = []
            for _ in range(n_iterations):
                pb(i)

                transactions = [SimulatedTransaction(actors, 1000, 500, 60*60*24*30) 
                                for _ in range(n_txs)]

                wrapper = AggregatorWrapper(MultiAggregator, 
                    DividedLinearAggregator, pool=pool, func=selection_method, progress=False)
                wrapper.create_aggregators_from_tx_lists([transactions])
                agg = next(wrapper.aggregators)

                agg.iterate()

                costs.append(agg.result["result_cost"])

                i += 1

            average = Decimal(sum(costs) / len(costs))

            with open(SAVE_NAME % ("result_matrix", "txt"), "a") as f:
                f.write("%s\t" % format(average, ".3e"))
            
        with open(SAVE_NAME % ("result_matrix", "txt"), "a") as f:            
            f.write("\n")

