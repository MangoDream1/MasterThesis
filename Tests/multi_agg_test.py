from data.reader import create_transactions, select_on_timestamp, select_on_block_height

from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Aggregator.MultiAggregator import MultiAggregator

def method(agg):
    agg.iterate(agg.get_crosses)
    for x in [3, 4, 5, 6]:
        agg.iterate(agg.get_loop, x)
        
if __name__ == "__main__":
    BLOCK_HEIGHTS = [496114, 496150]
    TIMESTAMPS    = [1511704262, 1511781118]


    selection = select_on_block_height(*BLOCK_HEIGHTS, 2)

    # wrapper = SimulatedAggregatorWrapper(MultiAggregator, 300, 500, DividedLinearAggregator, func=method)

    wrapper = AggregatorWrapper(MultiAggregator, DividedLinearAggregator, func=method)
    wrapper.create_aggregators_from_selections([selection])

    agg = next(wrapper.aggregators)

    print(agg.cost(agg.matrix), agg.matrix.shape)

    agg.iterate()

    print(wrapper.result[0])

    agg.plot_log_data()
