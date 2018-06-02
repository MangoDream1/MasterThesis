from data.reader import create_transactions, select_on_timestamp, select_on_block_height

from AggregatorWrapper.AggregatorWrapper import AggregatorWrapper
from AggregatorWrapper.SimulatedAggregatorWrapper import SimulatedAggregatorWrapper
from Aggregator.DividedLinearAggregator import DividedLinearAggregator
from Aggregator.MultiAggregator import MultiAggregator

if __name__ == "__main__":
    BLOCK_HEIGHTS = [496114, 496150]
    TIMESTAMPS    = [1511704262, 1511781118]


    selection = select_on_block_height(*BLOCK_HEIGHTS, 2)

    # wrapper = SimulatedAggregatorWrapper(MultiAggregator, 6, 20, DividedLinearAggregator)

    wrapper = AggregatorWrapper(MultiAggregator, DividedLinearAggregator, non_improvement=5)
    wrapper.create_aggregators_from_selections([selection])

    agg = next(wrapper.aggregators)

    print(agg.cost(agg.matrix))

    agg.iterate()

    agg.plot_log_data()

    print(agg.matrix.toarray())