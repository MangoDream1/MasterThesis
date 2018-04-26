from Aggregator.Aggregator import Aggregator
from Objects.SimulatedTransaction import SimulatedTransaction


class SimulatedAggregator(Aggregator):
    def __init__(self, n_transactions, time_block, amount_actors,
                 transaction_cost=100, balance_diff_multiplier=10, **kwargs):
        self._create_actors(amount_actors)

        transactions = [SimulatedTransaction(self.actors, **kwargs)
                        for _ in range(n_transactions)]

        super().__init__(transactions, time_block,
                         transaction_cost=transaction_cost,
                         balance_diff_multiplier=balance_diff_multiplier)

    def _create_actors(self, amount_actors):
        """
        Creates the actors
        :param amount_actors: amount of actors generated
        :return:
        """
        self.actors = [hex(x) for x in range(amount_actors)]
