from collections import defaultdict


class Aggregator:
    def __init__(self, transactions, time_block):
        self.transactions = sorted(transactions, key=lambda x: x.timestamp)

        self.tx_block = defaultdict(list)
        self.end_balance = defaultdict(lambda: defaultdict(int))

        self.split_into_blocks(time_block)
        self.blocks_end_balance()

    def split_into_blocks(self, time_block):
        """
        Splits self.transactions into time blocks. If time_blocks not specified (either 0 or None), then all
        transactions put into the same block.
        :param time_block: size of each time block
        :return:
        """
        if time_block == 0 or not time_block:
            self.tx_block[0] = self.transactions
            del self.transactions
            return

        min_time, max_time = self.transactions[0].timestamp, self.transactions[-1].timestamp
        time = max_time - min_time
        amount = int(time / time_block)

        print(time)
        print(amount)

        for i, x in enumerate(range(amount)):
            limit = min_time + (i+1) * time_block

            while True:
                if self.transactions[0].timestamp < limit:
                    self.tx_block[i].append(self.transactions.pop(0))
                    continue

                break

    def blocks_end_balance(self):
        """
        Calculates the end balance for each actor in each block
        :return:
        """

        for k, v in self.tx_block.items():
            for tx in v:
                self.end_balance[k][tx.to] += tx.amount
                self.end_balance[k][tx.fr] -= tx.amount
