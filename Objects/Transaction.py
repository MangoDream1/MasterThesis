class Transaction:
    def __init__(self, to, fr, amount, timestamp):
        self.to = to
        self.fr = fr
        self.amount = amount
        self.timestamp = timestamp

    def get_graph_edge(self):
        return self.to, self.fr, self.amount

    def __str__(self):
        return "to: {0} from: {1} amount: {2} timestamp: {3}".format(self.to, self.fr, self.amount, self.timestamp)
