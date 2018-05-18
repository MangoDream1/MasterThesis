class Transaction:
    def __init__(self, to, fr, amount, timestamp, block_height=0):
        self.to = to
        self.fr = fr
        self.amount = int(amount)
        self.timestamp = int(timestamp)
        self.block_height = int(block_height)

    def get_graph_edge(self):
        return self.to, self.fr, self.amount

    def __str__(self):
        return "to: {0} from: {1} amount: {2} timestamp: {3} block_height: {4}".format(
            self.to, self.fr, self.amount, self.timestamp, self.block_height)
