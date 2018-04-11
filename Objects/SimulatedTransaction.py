from Objects.Transaction import Transaction
from random import *
import time


class SimulatedTransaction(Transaction):
    def __init__(self, actors, mean=1000, standard_deviation=500, timestamp_max=60*60*24*30):

        t, f = self._pick_actors(actors)

        super().__init__(t, f, self._generate_amount(mean, standard_deviation), self._generate_timestamp(timestamp_max))

    @staticmethod
    def _pick_actors(actors):
        t = choice(actors)
        f = choice(actors)

        while f == t:
            t = choice(actors)

        return t, f

    @staticmethod
    def _generate_amount(mean, standard_deviation):
        return abs(normalvariate(mean, standard_deviation))

    @staticmethod
    def _generate_timestamp(_max):
        return time.time() + randint(-_max/2, _max/2)
