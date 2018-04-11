from Aggregator.Aggregator import Aggregator
from Objects.SimulatedTransaction import SimulatedTransaction


class SimulatedAggregator(Aggregator):
    def __init__(self, n_transactions, time_block, amount_actors, **kwargs):
        self._create_actors(amount_actors)

        transactions = [SimulatedTransaction(self.actors, **kwargs)
                        for _ in range(n_transactions)]

        super().__init__(transactions, time_block)

    def _create_actors(self, amount_actors):
        """
        Creates the actors
        :param amount_actors: amount of actors generated
        :return:
        """
        self.actors = [hex(x) for x in range(amount_actors)]
